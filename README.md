# Adobe Hackathon - Round 1B Submission

##  Project Structure

```
Round1B/
├── app/
│   └── main.py                         # Main execution script
├── input/
│   ├── documents/                      # Input document files
│   └── input.json                      # Input JSON for task
├── output/
│   └── challenge1b_output.json         # Final output JSON (generated)
├── nltk_data/
│   └── tokenizers/
│       └── punkt/
│           └── punkt.zip              # NLTK punkt tokenizer data
├── pretrained_models/
│   └── all-MiniLM-L6-v2/              # Pretrained sentence embedding model
├── Dockerfile                          # Docker setup instructions
├── requirements.txt                    # Python dependencies
├── README.md                           # Project documentation
├── challenge1b_output.json             # Sample/Expected output (if applicable)
└── approach_explanation.md             # Description of methodology
```

---

## Getting Started

This project is containerized with Docker. The app reads data from the `/input` directory and generates structured JSON output in the `/output` directory.

###  Prerequisites

- Docker installed on your machine
- Linux/AMD64 compatible environment

---

##  Build and Run Instructions

### 1. **Build Docker Image**

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandom .
```

### 2. **Run Docker Container**

```bash
docker run --rm \
  -v "${PWD}/input:/app/input" \
  -v "${PWD}/output:/app/output" \
  --network none \
  mysolutionname:somerandom
```

>  `--network none` ensures no internet access for compliance with challenge constraints.

---

##  Methodology

Details of the approach used are documented in [`approach_explanation.md`](./approach_explanation.md).

- Utilizes NLTK for sentence tokenization (offline `punkt` tokenizer preloaded)
- Uses `all-MiniLM-L6-v2` from Sentence Transformers for semantic encoding
- Outputs predictions in the format required by `challenge1b_output.json`

---

##  Dependencies

All dependencies are listed in `requirements.txt`, including:

- `nltk`
- `sentence-transformers`
- `numpy`
- `scikit-learn`
- Others as required by the solution

The NLTK `punkt` tokenizer is downloaded and set manually to comply with offline use:

```python
import nltk
nltk.data.path.append('/root/nltk_data')
```

---

##  Output

The container will generate output at:

```
/output/challenge1b_output.json
```

Ensure this folder exists and is empty before running the container.

---

##  Author

- **Kanak, Kavya, Kartikey**
- For Adobe Hackathon Round 1B – Document Intelligence

---

##  License

This project is developed solely for the Adobe Hackathon and is not intended for public distribution.

```

---
