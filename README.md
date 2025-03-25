# Root Cause Analysis Project       


 python -m venv .venv


## Project Overview
This project implements a root cause analysis system using knowledge graphs and a chatbot interface for engineers.

## Project Structure
- `/docs`: Documentation including knowledge graph tools presentation
- `/data`: Data storage
  - `/structured`: Structured data for analysis
  - `/unstructured`: Unstructured data (PDFs, etc.)
- `/src`: Source code
  - `/data_processing`: Scripts for data processing and analysis
    - `structured_data_analysis.py`: Basic data analysis for structured data
    - `excel_metadata_processor.py`: Processor for Excel files with metadata detection
    - `process_excel_data.py`: Command-line utility for Excel processing
  - `/knowledge_graph`: Knowledge graph implementation
  - `/chatbot`: Azure-based chatbot for engineers
- `/config`: Configuration files
- `/tests`: Testing scripts and test data

## Project Phases
1. Knowledge graph tools evaluation and presentation
2. Structured data analysis
   - Processing of hierarchical Excel data including metadata detection
   - Correlation and relationship analysis
3. Unstructured data (PDF) integration
4. Azure chatbot development

## Excel Metadata Processor

The Excel metadata processor (`excel_metadata_processor.py`) provides functionality to:

- Extract hierarchical data from complex Excel files
- Detect and extract metadata sections at the top of Excel files
- Handle merged cells across rows and columns
- Convert Excel data into properly structured JSON

### Usage

To process Excel files, use the included command-line utility:

```bash
# Process a single file
python src/data_processing/process_excel_data.py --single -i data/structured/your_file.xlsx -o data/processed/output.json

# Process all Excel files in a directory
python src/data_processing/process_excel_data.py --batch -i data/structured -o data/processed
```

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Configure Azure services in `config/config.yaml`
3. Run data processing scripts to build the knowledge graph
4. Deploy the chatbot to Azure

## Dependencies
See `requirements.txt` for a complete list of dependencies. 