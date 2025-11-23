#!/usr/bin/env python3
"""
1. Download/Clone this Repository/Folder. 
2. Drag your PDFs or folder of PDFs into the input_pdfs folder.  
3. Optional: Add/remove adjectives list in adjectives.txt file. 
4. Run this file: python3 pdf_adjective_counter.py. 
5. This will generate output file- results.xlsx. 

"""

import os
import re
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple, Iterable, Optional

try:
    import pandas as pd
    import PyPDF2
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# ========= Input/Output SETTINGS ========================
INPUT_PATHS = ["./input_pdfs"]
OUTPUT_FILE = "results.xlsx"
EXCLUDE_REFERENCES = True  # set to False to count within references/appendices
VERBOSE = True  # set to False for quiet mode

# ========= END USER SETTINGS ==================================================

# Default adjectives we identified as AI indicators
DEFAULT_ADJECTIVES = [
    "commendable","innovative","meticulous","intricate","notable",
    "versatile","noteworthy","invaluable","pivotal","potent",
    "fresh","ingenious","cogent","ongoing","tangible",
    "profound","methodical","laudable","lucid","appreciable",
    "fascinating","adaptable","admirable","refreshing","proficient",
    "intriguing","thoughtful","credible","exceptional","digestible",
    "prevalent","interpretative","remarkable","seamless","economical",
    "proactive","interdisciplinary","sustainable","optimizable","comprehensive",
    "vital","pragmatic","comprehensible","unique","fuller",
    "authentic","foundational","distinctive","pertinent","valuable",
    "invasive","speedy","inherent","considerable","holistic",
    "insightful","operational","substantial","compelling","technological",
    "beneficial","excellent","keen","cultural","unauthorized",
    "strategic","expansive","prospective","vivid","consequential",
    "manageable","unprecedented","inclusive","asymmetrical","cohesive",
    "replicable","quicker","defensive","wider","imaginative",
    "traditional","competent","contentious","widespread","environmental",
    "instrumental","substantive","creative","academic","sizeable",
    "extant","demonstrable","prudent","practicable","signatory",
    "continental","unnoticed","automotive","minimalistic","intelligent",
]

# Reference section patterns
_REFERENCE_HEADINGS = (
    r"References?",
    r"Bibliograph(?:y|ies)",
    r"Works\s+Cited",
    r"Literature\s+Cited",
    r"Citations?",
    r"Sources?",
    r"References\s+and\s+Notes",
    r"Notes",
    r"Endnotes",
    r"Footnotes",
    r"Appendix(?:es)?",
    r"Supplementar(?:y|ies)\s+Materials?",
    r"Supplemental\s+Materials?",
)

_REFERENCE_SPLIT_RX = re.compile(
    r"(?im)^\s*(?:\d+\.?|[IVXLC]+\.?)?\s*(?:" + r"|".join(_REFERENCE_HEADINGS) + r")\s*[:\-–—]?\s*$"
)

# ==============================================================================
# LOGGING
# ==============================================================================

class Logger:
    """Simple logger with verbosity control and colored output."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        # Check if terminal supports colors
        self.use_color = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _colorize(self, text: str, color_code: str) -> str:
        """Add color to text if terminal supports it."""
        if self.use_color:
            return f"\033[{color_code}m{text}\033[0m"
        return text
    
    def log(self, msg: str, force: bool = False):
        """Log a timestamped message."""
        if self.verbose or force:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] {msg}")
    
    def success(self, msg: str):
        """Log a success message in green."""
        msg = self._colorize(f"✓ {msg}", "32")
        self.log(msg, force=True)
    
    def warn(self, msg: str):
        """Log a warning in yellow."""
        msg = self._colorize(f"⚠ WARNING: {msg}", "33")
        self.log(msg, force=True)
    
    def error(self, msg: str):
        """Log an error in red."""
        msg = self._colorize(f"✗ ERROR: {msg}", "31")
        self.log(msg, force=True)
    
    def progress(self, current: int, total: int, msg: str):
        """Log progress information."""
        self.log(f"[{current}/{total}] {msg}")

# Global logger instance
logger = Logger(VERBOSE)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def natural_sort_key(s: str):
    """Generate key for natural sorting of filenames."""
    parts = re.split(r"(\d+)", s)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

def load_adjectives_from_file(path: str = "adjectives.txt") -> List[str]:
    """
    Load adjectives from file. One word per line, '#' for comments.
    Returns default list if file doesn't exist or is empty.
    """
    filepath = os.path.abspath(os.path.expanduser(path))
    
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                words = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        words.append(line.lower())
                
                if words:
                    logger.log(f"Loaded {len(words)} adjectives from {filepath}")
                    return words
                else:
                    logger.warn(f"{filepath} exists but is empty. Using defaults.")
        except Exception as e:
            logger.warn(f"Could not read {filepath}: {e}. Using defaults.")
    else:
        logger.log(f"No custom adjectives file found. Using {len(DEFAULT_ADJECTIVES)} defaults.")
    
    return DEFAULT_ADJECTIVES[:]

def strip_references(text: str) -> str:
    """
    Remove references and appendices from text.
    Uses both pattern matching and heuristics.
    """
    # Try pattern matching first
    for match in _REFERENCE_SPLIT_RX.finditer(text):
        return text[:match.start()]
    
    # Heuristic approach
    lines = text.splitlines()
    
    def looks_like_reference(line: str) -> bool:
        """Check if a line looks like a reference entry."""
        line = line.strip()
        if not line:
            return False
        
        # Common reference patterns
        patterns = [
            r"^[\[(]?\s*\d{1,3}[\])\.]?\s+",  # [1], (1), 1.
            r"\b(19\d{2}|20\d{2})\b.*[,\.;]",  # Year with punctuation
            r"doi:|https?://doi\.org/",         # DOI
            r"\bet al\.",                       # et al.
            r"\b\d{2,4}\s*[–\-]\s*\d{2,4}\b",  # Page ranges
        ]
        
        return any(re.search(pat, line, re.IGNORECASE) for pat in patterns)
    
    # Sliding window detection
    window_size, threshold = 4, 3
    for i in range(len(lines)):
        window = lines[i:i + window_size]
        if sum(looks_like_reference(line) for line in window) >= threshold:
            return "\n".join(lines[:i])
    
    # Fallback: check for "references" in latter half
    text_lower = text.lower()
    ref_pos = text_lower.find("references")
    if ref_pos != -1 and ref_pos > len(text) * 0.5:
        return text[:ref_pos]
    
    return text

# ==============================================================================
# PDF PROCESSING
# ==============================================================================

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extract text from PDF file.
    Returns (text, page_count).
    """
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            page_count = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                except Exception as e:
                    logger.warn(f"Could not extract page {page_num}: {e}")
                    continue
            
            return text, page_count
            
    except Exception as e:
        logger.error(f"Could not read {pdf_path}: {e}")
        return "", 0

def count_adjectives(text: str, adjectives: List[str]) -> Tuple[Dict[str, int], int]:
    """
    Count occurrences of each adjective in text.
    Returns (counts_dict, total_count).
    """
    counts = {}
    for adj in adjectives:
        pattern = r"\b" + re.escape(adj) + r"\b"
        matches = re.findall(pattern, text, re.IGNORECASE)
        counts[adj] = len(matches)
    
    total = sum(counts.values())
    return counts, total

def iter_pdf_files(input_path: str) -> Iterable[Tuple[str, str]]:
    """
    Iterate over PDF files
    """
    input_path = os.path.abspath(os.path.expanduser(input_path))
    
    # Single PDF file
    if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        folder = os.path.basename(os.path.dirname(input_path)) or "."
        yield (folder, input_path)
        return
    
    # Directory of PDFs (including all subfolders)
    if os.path.isdir(input_path):
        # Walk through input_path and all its subdirectories
        for root, dirs, files in os.walk(input_path):
            # Use the last part of the folder path as the "Folder" label
            folder_name = os.path.basename(root) or os.path.basename(input_path)

            pdf_files = sorted(
                [f for f in files if f.lower().endswith(".pdf")],
                key=natural_sort_key
            )

            for filename in pdf_files:
                yield (folder_name, os.path.join(root, filename))
        return

    
    raise FileNotFoundError(f"Path not found or not a PDF/folder: {input_path}")

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def process_pdfs(input_paths: List[str], adjectives: List[str], 
                 exclude_refs: bool = True) -> List:
    """
    Process all PDFs from input paths.
    Returns list of (folder, filename, pages, counts, total) tuples.
    """
    # Collect all PDF files
    jobs = []
    for path in input_paths:
        try:
            for folder, pdf_path in iter_pdf_files(path):
                jobs.append((folder, pdf_path))
        except FileNotFoundError as e:
            logger.warn(str(e))
            continue
    
    if not jobs:
        logger.error("No PDF files found to process.")
        return []
    
    logger.log(f"Found {len(jobs)} PDF file(s) from {len(input_paths)} input path(s)")
    
    # Process each PDF
    results = []
    start_time = time.time()
    
    for i, (folder, pdf_path) in enumerate(jobs, 1):
        filename = os.path.basename(pdf_path)
        logger.progress(i, len(jobs), f"Processing: {filename}")
        
        # Extract text
        text, pages = extract_text_from_pdf(pdf_path)
        if not text:
            logger.warn(f"No text extracted from {filename}")
            continue
        
        if pages:
            logger.log(f"  Pages: {pages}")
        
        # Optionally strip references
        if exclude_refs:
            original_len = len(text)
            text = strip_references(text)
            pct_removed = (1 - len(text)/original_len) * 100 if original_len > 0 else 0
            logger.log(f"  References excluded ({pct_removed:.1f}% removed)")
        
        # Count adjectives
        counts, total = count_adjectives(text, adjectives)
        logger.log(f"  Total adjectives found: {total}")
        
        results.append((folder, filename, pages, counts, total))
    
    elapsed = time.time() - start_time
    logger.success(f"Processed {len(results)} file(s) in {elapsed:.1f} seconds")
    
    return results

def export_to_excel(results: List, output_file: str, adjectives: List[str]):
    """Export results to Excel workbook with two sheets."""
    logger.log("Generating Excel report...")
    
    # Prepare data
    data = []
    for folder, filename, pages, counts, total in results:
        row = {
            "Folder": folder,
            "Article": filename, 
            "Pages": pages
        }
        row.update(counts)
        row["Total"] = total
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure all adjective columns exist
    for adj in adjectives:
        if adj not in df.columns:
            df[adj] = 0
    
    # Reorder columns
    column_order = ["Folder", "Article", "Pages"] + adjectives + ["Total"]
    df = df[column_order]
    
    # Calculate statistics by folder
    stats_df = df.groupby("Folder")["Total"].agg([
        ("Average Total", "mean"),
        ("Std Dev", "std"),
        ("Min", "min"),
        ("Max", "max"),
        ("Count", "count")
    ]).round(2)
    
    # Ensure output directory exists
    output_path = os.path.abspath(os.path.expanduser(output_file))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Write to Excel
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        # Results sheet
        df.to_excel(writer, sheet_name="Results", index=False)
        
        # Statistics sheet  
        stats_df.to_excel(writer, sheet_name="Statistics")
        
        # Add formatting
        workbook = writer.book
        results_sheet = writer.sheets["Results"]
        stats_sheet = writer.sheets["Statistics"]
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E8E8E8',
            'border': 1
        })
        
        # Apply header formatting to Results sheet
        for col_num, value in enumerate(df.columns.values):
            results_sheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            results_sheet.set_column(i, i, min(max_len, 50))
    
    logger.success(f"Results saved to: {output_path}")
    logger.log(f"  • {len(results)} articles analyzed")
    logger.log(f"  • {len(stats_df)} folder(s) processed")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Main entry point for the script (simple mode only)."""
    global logger

    # Use USER SETTINGS from the top of the file
    input_paths = INPUT_PATHS
    output_file = OUTPUT_FILE
    exclude_refs = EXCLUDE_REFERENCES
    adjectives_file = "adjectives.txt"  # or change this if you want a different default
    verbose = VERBOSE

    if not input_paths:
        print("\n" + "=" * 60)
        print("ERROR: No input paths configured!")
        print("=" * 60)
        print("\nPlease edit the USER SETTINGS at the top of this script:")
        print("  1. Open pdf_adjective_counter.py in a text editor")
        print("  2. Set INPUT_PATHS to your PDF folder(s) or file(s)")
        print("  3. Set OUTPUT_FILE to where you want results saved")
        print("  4. Run: python3 pdf_adjective_counter.py")
        print("\nExample:")
        print("  INPUT_PATHS = [\"/Users/you/Documents/papers\"]")
        print("  OUTPUT_FILE = \"results.xlsx\"")
        print("=" * 60 + "\n")
        sys.exit(1)

    # Update logger verbosity
    logger = Logger(verbose)

    # Header
    logger.log("=" * 60)
    logger.log("PDF Adjective Counter for AI Detection")
    logger.log("=" * 60)

    # Ensure output has .xlsx extension
    if not output_file.lower().endswith(".xlsx"):
        output_file += ".xlsx"

    # Load adjectives (from adjectives.txt if present, otherwise defaults)
    adjectives = load_adjectives_from_file(adjectives_file)

    # Process PDFs
    results = process_pdfs(input_paths, adjectives, exclude_refs)

    if results:
        export_to_excel(results, output_file, adjectives)
        logger.log("=" * 60)
        logger.success("Analysis complete!")
    else:
        logger.error("No results to export.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
