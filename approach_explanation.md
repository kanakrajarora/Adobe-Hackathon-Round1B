## 🔍 Approach Explanation

Our solution aims to extract structured insights from a set of unstructured PDF documents. The core objective was to classify each line of text into appropriate sections such as `H1`, `H2`, `List-Item`, `Other`, etc., while also associating it with relevant metadata like font size, boldness, and content features. The pipeline is designed to be modular, efficient, and easily scalable.

---

### 📄 1. Document Preprocessing

We begin by loading the PDF documents using `pdfplumber`, which gives us access to text, font metadata, and positioning for each line. Each line is stripped of whitespace, and key features such as average font size, boldness, and whether the line starts with a number are extracted. These features form the basis for downstream classification.

---

### 💬 2. Feature Engineering

Each line of text is represented with a combination of:

- **Raw textual features** (e.g., line content, upper-case ratio, line length),
- **Visual features** (e.g., font size, boldness),
- **Semantic embeddings** using [SentenceTransformers](https://www.sbert.net/) model `"all-MiniLM-L6-v2"` for capturing contextual meaning of each line.

This hybrid representation of layout and content ensures robust learning of document structure.

---

### 🧠 3. Classification Model

A multi-layer perceptron (MLP) classifier is trained on labeled examples with inputs being a concatenation of semantic embeddings and engineered features. The model was trained outside the container environment and the weights were saved in a `pretrained_models` folder to avoid re-training during inference.

This approach avoids hand-crafted rule-based logic and leverages semantic similarity across documents to generalize better on unseen PDFs.

---

### 🧪 4. Inference Pipeline

At runtime, the model loads the input documents from the `/input` directory, extracts features, and classifies each line. The result is written as a JSON file into the `/output` directory. Each line in the output includes:

- `text`
- `label` (e.g., `H1`, `List-Item`, etc.)
- `page_num`
- extracted features for traceability

This structured output format is ideal for downstream NLP tasks or knowledge extraction.

---

### 🐳 5. Dockerization

The entire application is containerized to ensure consistency across environments. All dependencies are pinned in `requirements.txt`. To comply with the challenge’s offline execution constraints (`--network none`), we preloaded necessary NLP models (`punkt` tokenizer and sentence embedding model) during image build time.

---

### ✅ Conclusion

This approach combines layout-aware text processing with semantic embeddings, enabling accurate classification of diverse document formats. The modular pipeline, embedded model, and Dockerized packaging make the solution robust, reproducible, and adaptable to real-world applications.