# PDF-AI-detector
PDF Adjective Counter for AI-Generated Content Detection  
A research tool for detecting potential AI-generated text in academic PDFs by analyzing adjective frequency patterns.

## Features
- Analyze single PDFs or entire folders  
- Option to exclude references/appendices  
- Generates an Excel report with per-file counts and summary statistics  
- Works in simple mode (edit-and-run) or CLI  

## Installation
```bash
git clone https://github.com/yourusername/PDF-AI-detector.git
cd PDF-AI-detector
pip install -r requirements.txt
```

## Usage

1. Once you've completed installation, drag and drop your individual pdfs or folders of pdfs into the "input_pdfs" folder,
2. Optional: edit adjectives.txt file to change/add/remove any search terms
3. Run:

```bash
python3 pdf_adjective_counter.py
```

## Output

The script generates an Excel file named results.xlxs with:

### Sheet 1 – Results

Adjective counts per PDF.

### Sheet 2 – Summary Statistics

Average, min, max, and standard deviation per folder.

## Configuration (optional)

```python
EXCLUDE_REFERENCES = True     # remove references section
VERBOSE = True                # detailed terminal output
OUTPUT_FILE = "results.xlsx"  # path to results file
```
## Methodology Clarification

This code was used for adjective-frequency extraction step described in the Methods. Subsequent analyses were performed using the output Excel file.

## Associated Publication
An Evaluation of Current Trends in AI-Generated Text in Otolaryngology Publications.
Laryngoscope. 2025 Oct;135(10):3579–3587.
doi: 10.1002/lary.32202

## License

MIT License

## Acknowledgments

Research team
