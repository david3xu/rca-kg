# Excel to JSON Converter with Hierarchical Data Support

A powerful Python tool for converting complex Excel files to structured JSON, with special handling for:

- Hierarchical data with merged cells
- Metadata sections at the top of files
- Multiple worksheets
- Large file processing

## Features

- **Metadata Detection**: Automatically identifies header sections at the top of Excel files
- **Merged Cell Handling**: Correctly preserves parent-child relationships represented by merged cells
- **Type Preservation**: Maintains data types (numbers, dates, text) during conversion
- **Batch Processing**: Process multiple Excel files at once with optional caching
- **Multi-sheet Support**: Process multiple worksheets within a workbook
- **Memory Efficiency**: Chunk-based processing to handle large Excel files
- **Logging**: Comprehensive logging for tracking and debugging

## Installation

### Requirements

- Python 3.6+
- Required packages:
  - pandas
  - openpyxl
  - pathlib

Install the required packages:

```bash
pip install pandas openpyxl
```

## Usage

### Command Line Interface

#### Process a Single File

```bash
python excel_to_json.py single -i input.xlsx -o output.json
```

Options:
- `-i, --input`: Input Excel file (required)
- `-o, --output`: Output JSON file (required)
- `-s, --sheet`: Specific sheet to process
- `-m, --metadata-rows`: Maximum rows to check for metadata (default: 6)
- `-e, --include-empty`: Include empty cells in output

#### Process Multiple Sheets

```bash
python excel_to_json.py multi -i input.xlsx -o output.json -s Sheet1 Sheet3
```

Options:
- `-i, --input`: Input Excel file (required)
- `-o, --output`: Output JSON file (required)
- `-s, --sheets`: Names of sheets to process (if not specified, all sheets are processed)

#### Batch Processing

```bash
python excel_to_json.py batch -i input_directory -o output_directory -c
```

Options:
- `-i, --input-dir`: Directory containing Excel files (required)
- `-o, --output-dir`: Directory for JSON output (required)
- `-c, --cache`: Enable caching to avoid reprocessing unchanged files
- `--cache-dir`: Directory for cache files (default: '.cache')

### Programmatic Usage

```python
from excel_to_json import convert_hierarchical_excel, batch_process_excel_files, process_workbook

# Process a single file
result = convert_hierarchical_excel(
    'input.xlsx', 
    'output.json',
    config={
        'metadata_max_rows': 8,
        'include_empty_cells': True,
        'sheet_name': 'Data'
    }
)

# Process multiple sheets
result = process_workbook(
    'input.xlsx',
    'output.json',
    sheet_names=['Sheet1', 'Sheet2']
)

# Batch processing
results = batch_process_excel_files(
    'input_directory',
    'output_directory',
    use_cache=True
)
```

## Output Format

The JSON output includes metadata and hierarchical data:

```json
{
  "metadata": {
    "header_r1": "Document Title",
    "row_1": { "A": "Document ID", "B": "ABC123" },
    "row_2": { "A": "Date", "B": "2023-06-15" }
  },
  "data": [
    {
      "Category": "Equipment",
      "Item": {
        "value": "Pump",
        "sub_values": ["Model A", "Model B", "Model C"]
      },
      "Status": "Active"
    }
  ]
}
```

## Advanced Configuration

The script accepts a configuration dictionary with these options:

- `metadata_max_rows`: Maximum rows to scan for metadata (default: 6)
- `header_detection_threshold`: Minimum number of values to consider a row as header (default: 3)
- `sheet_name`: Specific sheet to process (default: active sheet)
- `include_empty_cells`: Whether to include null values (default: False)
- `chunk_size`: Number of rows to process at once for large files (default: 1000)

## Error Handling

The script uses custom exceptions to provide clear error messages:

- `ExcelProcessingError`: Base exception for all processing errors
- `MergeMapError`: Error building the merge map
- `MetadataExtractionError`: Error extracting metadata
- `DataExtractionError`: Error extracting data

## Limitations

- Complex conditional formatting is not preserved
- Formulas are processed as their calculated values
- Charts and images are not included in the JSON output

## Key Improvements Over Original Version

1. **Modular Architecture**: Code refactored into smaller, focused functions for better maintainability
2. **Robust Error Handling**: Custom exception hierarchy and comprehensive error logging
3. **Type Handling**: Preserves data types (numbers, dates, booleans) from Excel
4. **Memory Optimization**: Chunk-based processing for large files
5. **Caching System**: Avoids reprocessing unchanged files
6. **Multi-sheet Support**: Process specific sheets or entire workbooks
7. **Command-line Interface**: User-friendly CLI with sub-commands
8. **Comprehensive Logging**: Detailed logging for tracking and debugging

## License

MIT License
