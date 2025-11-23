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
git clone https://github.com/yourusername/pdf-adjective-counter.git
cd pdf-adjective-counter
pip install -r requirements.txt
```

## Usage

### Simple Mode (edit-and-run)

Edit paths at the top of the script:

```python
INPUT_PATHS = ["path/to/pdfs"]
OUTPUT_FILE = "results.xlsx"
EXCLUDE_REFERENCES = True
```

Run:

```bash
python3 pdf_adjective_counter.py
```

### CLI Mode

Analyze a file:

```bash
python3 pdf_adjective_counter.py article.pdf -o results.xlsx
```

Analyze a folder:

```bash
python3 pdf_adjective_counter.py papers/ -o results.xlsx
```

Include references:

```bash
python3 pdf_adjective_counter.py papers/ --include-refs
```

Use custom adjective list:

```bash
python3 pdf_adjective_counter.py papers/ --adjectives adjectives.txt
```

## Output

The script generates an Excel file with:

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

## Associated Publication
An Evaluation of Current Trends in AI-Generated Text in Otolaryngology Publications.
Laryngoscope. 2025 Oct;135(10):3579–3587.
doi: 10.1002/lary.32202

## License

MIT License

## Acknowledgments

Research team
