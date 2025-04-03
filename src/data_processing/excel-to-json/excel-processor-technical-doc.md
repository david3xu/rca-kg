# Excel to JSON Converter - Technical Documentation

## Architecture Overview

The Excel to JSON converter is structured as a modular, pipeline-oriented system that transforms complex Excel files into structured JSON. The implementation follows a functional decomposition pattern with stateless functions that handle specific tasks in the conversion process.

## Core Architecture Principles

1. **Pipeline Processing**: Data flows through a series of transformations from raw Excel to structured JSON
2. **Separation of Concerns**: Each function has a single responsibility
3. **Error Propagation**: Errors are captured, categorized, and propagated through a custom exception hierarchy
4. **Stateless Processing**: Functions don't maintain state between calls (except for caching)
5. **Configurability**: Behavior can be adjusted through configuration parameters

## Code Structure and Component Relationships

### High-Level Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Loading   │────▶│ Structure       │────▶│ Hierarchical    │
│  & Extraction   │     │ Detection       │     │ Data Processing │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                        │
         ▼                      ▼                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Result Construction & Output                  │
└──────────────────────────────────────────────────────────────────┘
```

### Function Relationships and Data Flow

The key functions and their relationships:

1. **Entry Points**:
   - `convert_hierarchical_excel`: Main single-file processing function
   - `batch_process_excel_files`: Directory batch processing
   - `process_workbook`: Multi-sheet processing

2. **Core Processing Pipeline**:
   - `load_workbook`: Loads Excel file
   - `build_merge_map`: Creates cell merge mapping
   - `extract_metadata`: Detects and extracts header information
   - `identify_data_start`: Determines where main data begins
   - `extract_hierarchical_data`: Processes main data section
   - `create_result_structure`: Combines metadata and main data
   - `write_json_output`: Writes result to file

3. **Utility Functions**:
   - `get_typed_cell_value`: Type-aware cell value extraction
   - `get_cell_value`: Merge-aware value retrieval
   - `get_file_hash`: Generates file hash for caching

## Key Algorithms and Technical Details

### Merge Map Construction

The merge map is a dictionary mapping `(row, col)` coordinates to information about merged cells:

```python
# Structure of a merge_map entry
merge_map[(row, col)] = {
    'value': cell_value,      # Value from the top-left cell
    'origin': (min_row, min_col),  # Origin coordinates of the merge
    'range': str(merged_range)  # String representation for debugging
}
```

This approach creates an O(1) lookup for any cell position to determine if it's part of a merged region. The algorithm examines each merged range and creates entries for every cell within it, pointing back to the top-left cell. This enables efficient traversal while preserving hierarchical relationships.

Time complexity: O(M * C) where M is the number of merged regions and C is the average number of cells per merged region.

### Metadata Detection Algorithm

The metadata detection uses a two-phase approach:

1. **Header Section Detection**:
   ```python
   if (merged_range.min_row <= 3 and (merged_range.max_col - merged_range.min_col + 1) > 2):
       # This is likely a header section
   ```

   This identifies large merged cells at the top of the document that typically indicate title/header sections.

2. **Metadata Row Detection**:
   ```python
   for row in range(1, min(max_metadata_rows + 1, max_row + 1)):
       # Check for key-value pairs or structured information
   ```

   This scans the top rows for structured information, often in key-value format.

The algorithm adapts to different Excel layouts by detecting both large merged headers and structured row-based metadata.

### Hierarchical Data Extraction

The hierarchical data extraction algorithm traverses the sheet row by row, handling the complex case of merged cells that represent parent-child relationships:

1. **Skip Already Processed Rows**:
   ```python
   if row_idx in rows_processed:
       row_idx += 1
       continue
   ```

2. **Detect Merged Cell Origins**:
   ```python
   if cell_key in merge_map and merge_map[cell_key]['origin'] == cell_key:
       # This is a merged cell origin - handle specially
   ```

3. **Process Parent-Child Relationships**:
   ```python
   if col_idx > 0:  # Not the first column
       sub_values = []
       for sub_row in range(row_idx, row_idx + skip_rows):
           # Collect values in child rows
   ```

This recursive traversal preserves hierarchical relationships where a parent cell (merged vertically) has multiple child values in adjacent columns.

Time complexity: O(R * C) where R is the number of rows and C is the number of columns.

### Type-Aware Value Extraction

The converter preserves original data types through type detection:

```python
def get_typed_cell_value(cell):
    if cell.value is None:
        return None
        
    if cell.data_type == 'n':  # Number
        return float(cell.value) if isinstance(cell.value, float) else int(cell.value)
    elif cell.data_type == 'd':  # Date
        return cell.value.isoformat() if hasattr(cell.value, 'isoformat') else str(cell.value)
    elif cell.data_type == 'b':  # Boolean
        return bool(cell.value)
    
    # Default to string for other types
    return str(cell.value) if cell.value is not None else None
```

This ensures that numbers remain numbers, dates are ISO-formatted, and booleans are preserved as boolean values in the resulting JSON.

### Chunk-Based Processing for Memory Efficiency

To handle large Excel files, the extraction processes data in chunks:

```python
for chunk_start in range(data_start_row-1, max_row, chunk_size):
    chunk_end = min(chunk_start + chunk_size, max_row)
    logger.debug(f"Processing rows {chunk_start+1} to {chunk_end}")
    
    # Process row by row within this chunk
    row_idx = chunk_start
    while row_idx < chunk_end:
        # Process row
```

This approach prevents loading the entire sheet into memory at once, which would be problematic for very large files.

Memory complexity is reduced from O(R * C) to O(chunk_size * C) where R is the total number of rows and C is the number of columns.

### Caching System Implementation

The caching system uses file hashing to detect changes:

```python
def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()
```

This generates a unique hash based on file content. The batch processor then uses this hash to determine if a file has changed:

```python
file_hash = get_file_hash(str(excel_file))
cache_file = os.path.join(cache_dir, f"{excel_file.stem}_{file_hash}.pkl")

if os.path.exists(cache_file):
    # Use cached result
    with open(cache_file, 'rb') as f:
        result = pickle.load(f)
    process_file = False
```

The chunked reading pattern (64KB at a time) ensures that even very large files can be hashed efficiently without loading the entire file into memory.

## Error Handling System

The code implements a custom exception hierarchy:

```
ExcelProcessingError (base)
├── MergeMapError
├── MetadataExtractionError
└── DataExtractionError
```

Each function catches specific exceptions and wraps them in the appropriate exception type:

```python
try:
    merge_map = build_merge_map(sheet)
except Exception as e:
    logger.error(f"Failed to build merge map: {str(e)}")
    raise MergeMapError(f"Failed to build merge map: {str(e)}") from e
```

This provides clear error categorization and maintains the original exception context through exception chaining with the `from e` syntax.

## Configuration System

The configuration system uses a dictionary-based approach with defaults:

```python
# Parse configuration
config = config or {}
metadata_max_rows = config.get('metadata_max_rows', 6)
header_threshold = config.get('header_detection_threshold', 3)
sheet_name = config.get('sheet_name')
include_empty = config.get('include_empty_cells', False)
chunk_size = config.get('chunk_size', 1000)
```

This pattern provides flexibility without requiring all parameters to be specified. The configuration propagates through the function calls where needed, affecting behavior at specific processing points.

## Multi-Sheet Processing Implementation

The multi-sheet processing maintains a nested structure in the resulting JSON:

```python
result = {"sheets": {}}
for sheet_name in sheets_to_process:
    if sheet_name in wb.sheetnames:
        logger.info(f"Processing sheet: {sheet_name}")
        sheet_config = config.copy() if config else {}
        sheet_config['sheet_name'] = sheet_name
        
        # Don't write individual JSON files for sheets
        sheet_data = convert_hierarchical_excel(excel_file, None, sheet_config)
        result["sheets"][sheet_name] = sheet_data
```

The individual sheet processing reuses the same core function (`convert_hierarchical_excel`) but specifies `None` for the JSON output file to prevent writing individual files. The results are collected in memory and written as a single combined file at the end.

## Command-Line Interface Design

The CLI uses argparse with subcommands to provide a user-friendly interface:

```python
parser = argparse.ArgumentParser(description='Convert Excel files with complex hierarchical data to JSON')
subparsers = parser.add_subparsers(dest='command', help='Command to run')

# Single file processing
single_parser = subparsers.add_parser('single', help='Process a single Excel file')
# ...

# Multi-sheet processing
multi_parser = subparsers.add_parser('multi', help='Process multiple sheets in an Excel file')
# ...

# Batch processing
batch_parser = subparsers.add_parser('batch', help='Process all Excel files in a directory')
# ...
```

This approach creates a structured command hierarchy that maps to the three main processing modes, with mode-specific options for each.

## Performance Considerations

Several techniques optimize performance:

1. **Merge Map**: O(1) lookups for merged cell information
2. **Chunked Processing**: Reduces memory footprint for large files
3. **Caching**: Avoids redundant processing of unchanged files
4. **Selective Processing**: Only processes data rows, skipping already processed rows
5. **Type Preservation**: Minimizes unnecessary type conversions

## Extension Points

The code is designed with several extension points:

1. **Custom Cell Processing**: Extend `get_typed_cell_value` for specialized type handling
2. **Additional Metadata Extraction**: Enhance `extract_metadata` for domain-specific metadata
3. **Alternative Output Formats**: Modify `write_json_output` for different output formats
4. **Custom Progress Reporting**: Add callback parameters for progress updates
5. **Validation Rules**: Add data validation during the extraction process

## Threading and Concurrency

The current implementation is single-threaded. Potential concurrency improvements could include:

1. **Parallel Batch Processing**: Process multiple files concurrently
2. **Concurrent Sheet Processing**: Process multiple sheets in parallel
3. **Producer-Consumer Pattern**: Extract data in one thread while writing JSON in another

These would require thread safety considerations, particularly for logging and progress reporting.

## Logging Implementation

The code uses Python's built-in logging module with a configurable level:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("excel_processing.log"), logging.StreamHandler()]
)
logger = logging.getLogger("excel_processor")
```

This provides both console output and file-based logging, with timestamps and severity levels. Each function uses appropriate log levels:

- `logger.info()`: Normal operational information
- `logger.warning()`: Potential issues that don't prevent completion
- `logger.error()`: Errors that prevent a specific operation
- `logger.debug()`: Detailed diagnostic information
