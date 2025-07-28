import os
import json
import time
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
import nltk
nltk.data.path.append('/root/nltk_data')
from collections import defaultdict
from heapq import nlargest

# Load sentence transformer for semantic similarity
model = SentenceTransformer("/app/pretrained_models/all-MiniLM-L6-v2")

# Extract text from all pages of a PDF
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    doc_text = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            doc_text.append((page_num + 1, text.strip()))
    return doc_text

# Chunk text into sections based on headers or numeric prefixes
def chunk_sections(pages):
    sections = []
    current_section = {"title": "Introduction", "content": "", "page": 1}
    for page_num, text in pages:
        lines = text.split("\n")
        for line in lines:
            clean = line.strip()
            if clean.isupper() or clean.startswith(tuple("123456789")):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": clean, "content": "", "page": page_num}
            else:
                current_section["content"] += line + " "
    if current_section["content"]:
        sections.append(current_section)
    return sections

# Rank each section by semantic similarity to job description
def rank_sections(sections, job_desc):
    job_embedding = model.encode(job_desc, convert_to_tensor=True)
    ranked_sections = []
    for sec in sections:
        sec_embedding = model.encode(sec["content"], convert_to_tensor=True)
        score = util.pytorch_cos_sim(job_embedding, sec_embedding).item()
        ranked_sections.append((score, sec))
    ranked_sections.sort(key=lambda x: x[0], reverse=True)
    return ranked_sections

# Extract top-k most informative sentences from section
def summarize_text(text, top_k=3):
    sentences = nltk.sent_tokenize(text)
    word_freq = defaultdict(int)
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word.isalpha():
                word_freq[word] += 1

    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq[word.lower()] for word in nltk.word_tokenize(sentence) if word.isalpha())
        sentence_scores.append((score, sentence))

    summary = " ".join([s for _, s in nlargest(top_k, sentence_scores)])
    return summary

# Select top diverse sections (no document repetition)
def select_diverse_top_sections(all_sections, max_total=5):
    picked = []
    seen_docs = set()
    for score, section in sorted(all_sections, key=lambda x: x[0], reverse=True):
        doc = section.get("doc_title")
        if doc not in seen_docs:
            picked.append((score, section))
            seen_docs.add(doc)
        if len(picked) >= max_total:
            break
    return picked

# Assemble final JSON structure
def generate_output(document_sections, persona, job, challenge_info):
    output = {
        "challenge_info": challenge_info,
        "metadata": {
            "input_documents": list(document_sections.keys()),
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "extracted_sections": [],
        "sub_section_analysis": []
    }

    all_ranked = []
    for doc_title, ranked in document_sections.items():
        for score, sec in ranked[:7]:  # Pick top N from each doc
            sec["doc_title"] = doc_title
            all_ranked.append((score, sec))

    top_sections = select_diverse_top_sections(all_ranked, max_total=5)

    for rank, (_, section) in enumerate(top_sections, 1):
        output["extracted_sections"].append({
            "document": section["doc_title"],
            "page_number": section["page"],
            "section_title": section["title"],
            "importance_rank": rank
        })

        summary = summarize_text(section["content"], top_k=3)

        output["sub_section_analysis"].append({
            "document": section["doc_title"],
            "refined_text": summary,
            "page_number": section["page"]
        })

    return output

# Main function
def main():
    input_json_path = os.path.join("input", "input.json")
    documents_path = os.path.join("input", "documents")
    output_path = os.path.join("output", "challenge1b_output.json")

    with open(input_json_path) as f:
        input_data = json.load(f)

    challenge_info = input_data.get("challenge_info", {})
    persona = input_data.get("persona", {}).get("role", "") or input_data.get("metadata", {}).get("persona", "")
    job = input_data.get("job_to_be_done", {}).get("task", "") or input_data.get("metadata", {}).get("job_to_be_done", "")
    documents = input_data.get("documents", []) or input_data.get("metadata", {}).get("input_documents", [])

    document_sections = {}

    for doc_entry in documents:
        if isinstance(doc_entry, dict):
            filename = doc_entry.get("filename")
            title = doc_entry.get("title", filename)
        else:
            filename = doc_entry
            title = filename.replace(".pdf", "").replace("_", " ").strip()

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        path = os.path.join(documents_path, filename)
        if not os.path.exists(path):
            print(f"Warning: {filename} not found.")
            continue

        pages = extract_pdf_text(path)
        sections = chunk_sections(pages)
        ranked = rank_sections(sections, job)
        document_sections[title] = ranked

    output = generate_output(document_sections, persona, job, challenge_info)

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Write to output JSON
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(output, out_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()



