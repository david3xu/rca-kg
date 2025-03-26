# Root Cause Analysis Knowledge Graph

## Project Overview

This project implements a comprehensive root cause analysis (RCA) system using knowledge graph technology, integrated with machine learning components and a chatbot interface for engineers. Knowledge graphs provide an ideal framework for RCA by representing complex system relationships in a structured, navigable format that facilitates causal reasoning.

Key advantages of the knowledge graph approach include:

- **Unified representation** of equipment, components, symptoms, and causes
- **Explicit modeling** of causal and hierarchical relationships
- **Integration of structured and unstructured data** into a coherent framework
- **Inference capabilities** through graph traversal and analysis algorithms
- **Decision support** through ranked root cause identification and visualization

## Project Structure

```
/
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── structured/         # Structured data sources
│   └── unstructured/       # Unstructured data (PDFs, etc.)
├── docs/                   # Documentation
│   ├── guidelines/         # Implementation guides
│   ├── knowledge_graph/    # Literature review on KG for RCA
│   └── knowledge_graph_tools.md  # Tools evaluation
├── models/                 # Trained model storage
├── notebooks/              # Jupyter notebooks for exploration
│   ├── kg_fundamentals/    # Knowledge graph fundamentals
│   ├── ml_for_kg/          # ML integration for knowledge graphs
│   └── tool_comparison/    # Tool evaluation notebooks
├── src/                    # Source code
│   ├── chatbot/            # Azure-based chatbot interface
│   ├── data_processing/    # Data processing components
│   │   ├── structured_data_analysis.py  # Basic data analysis
│   │   ├── excel_metadata_processor.py  # Excel data extraction
│   │   ├── process_excel_data.py        # Command-line utility
│   │   └── create_kg_excel.py           # KG to Excel export
│   ├── evaluation/         # Evaluation metrics and tools
│   └── knowledge_graph/    # Core KG implementation
│       ├── algorithms/     # Graph algorithms
│       │   └── traversal.py  # Path finding and traversal
│       ├── graph_builder.py  # Main graph construction
│       ├── inference/      # Inference engines
│       │   ├── causal_inference.py    # Causal path analysis
│       │   └── root_cause_ranking.py  # Root cause prioritization
│       ├── ml/             # Machine learning components
│       │   ├── entity_extraction/     # Entity identification
│       │   └── relationship_prediction/  # Relationship extraction
│       └── schema/         # Ontology and schema definitions
└── tests/                  # Testing scripts
```

## Technical Components

### 1. Knowledge Graph Construction

The system builds a knowledge graph with four primary entity types:
- **Equipment**: Physical machinery and devices
- **Components**: Parts that make up equipment
- **Symptoms**: Observable indications of issues
- **Root Causes**: Underlying causes of problems

Relationships between these entities include:
- **CONTAINS**: Equipment contains components
- **EXHIBITS**: Equipment or components exhibit symptoms
- **CAUSES**: Root causes lead to symptoms
- **RELATES_TO**: General associations between entities

The `graph_builder.py` module handles the core graph construction, supporting both manual definition and automated generation from processed data sources.

### 2. Data Processing Pipeline

#### Structured Data Analysis

The `structured_data_analysis.py` module provides functionality to:
- Load and clean structured data from CSV, Excel, or JSON files
- Identify correlations and potential causal relationships
- Export relationship data for knowledge graph construction

#### Excel Metadata Processor

The Excel metadata processor (`excel_metadata_processor.py`) provides specialized functionality to:
- Extract hierarchical data from complex Excel files
- Detect and extract metadata sections at the top of Excel files
- Handle merged cells across rows and columns
- Convert Excel data into properly structured JSON for KG integration

### 3. Machine Learning Integration

The ML components enhance knowledge graph construction through:

#### Entity Extraction

The `entity_extraction` module identifies entities from unstructured text using:
- Rule-based identification for known entity types
- ML-based extraction for complex or ambiguous entities
- Entity classification and normalization

#### Relationship Prediction

The `relationship_prediction` module determines relationships between entities using:
- Pattern-based extraction from text
- Co-occurrence analysis
- ML-based relationship classification
- Confidence scoring for extracted relationships

### 4. Inference Engines

The inference components provide root cause identification through:

#### Causal Inference

The `causal_inference.py` module implements:
- Path finding between symptoms and potential causes
- Path strength calculation based on relationship types and confidence
- Multi-factor causal analysis incorporating temporal aspects when available

#### Root Cause Ranking

The `root_cause_ranking.py` module prioritizes potential causes using:
- Causal confidence scores
- Centrality in the knowledge graph
- Historical frequency of association with the symptom
- Severity impact
- Resolution difficulty

### 5. Azure Chatbot Interface

The `azure_bot.py` module provides a natural language interface that:
- Allows engineers to query the knowledge graph
- Translates natural language questions into graph queries
- Returns root cause analysis results with explanations
- Integrates with Azure Cognitive Services

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Azure services (if using the chatbot):
```bash
# Copy and modify the example configuration
cp config/config.yaml.example config/config.yaml
# Edit the configuration file with your Azure service credentials
```

4. Process data and build the knowledge graph:
```bash
# Process structured data
python src/data_processing/process_excel_data.py --batch -i data/structured -o data/processed

# Build the knowledge graph
python src/knowledge_graph/graph_builder.py
```

## Usage Examples

### Data Processing

Process Excel files with the command-line utility:

```bash
# Process a single file
python src/data_processing/process_excel_data.py --single -i data/structured/your_file.xlsx -o data/processed/output.json

# Process all Excel files in a directory
python src/data_processing/process_excel_data.py --batch -i data/structured -o data/processed
```

### Root Cause Analysis

Perform root cause analysis for a specific symptom:

```bash
# Analyze causes for a specific symptom
python src/knowledge_graph/inference/causal_inference.py --symptom "Vibration" --graph data/knowledge_graph/graph.json
```

### Tool Exploration

Explore different knowledge graph tools with the provided notebooks:

```bash
cd notebooks/tool_comparison
jupyter notebook
```

## Documentation

Detailed documentation is available in the `/docs` directory:

- [Knowledge Graph Implementation Guide](docs/guidelines/knowledge-graph-impl-guide.md): Comprehensive implementation instructions
- [Knowledge Graph Literature Review](docs/knowledge_graph/literature_review/README.md): Background and theoretical foundations
- [Knowledge Graph Tools Evaluation](docs/knowledge_graph_tools.md): Comparison of available technologies

## Project Phases

The project has been implemented in four phases:

1. **Knowledge Graph Tools Evaluation**
   - Comparative analysis of Neo4j, NetworkX, and other tools
   - Selection of appropriate technologies

2. **Structured Data Analysis**
   - Processing of hierarchical Excel data with metadata detection
   - Correlation and relationship analysis
   - Integration into knowledge graph structure

3. **Machine Learning Integration**
   - Entity extraction from unstructured text
   - Relationship prediction and confidence scoring
   - Knowledge graph enrichment

4. **Azure Chatbot Development**
   - Natural language interface for engineers
   - Integration with Azure Cognitive Services
   - Presentation of root cause analysis results

## Testing

Run the test suite to verify functionality:

```bash
python -m unittest discover tests
```

## Dependencies

The system relies on the following key dependencies:
- `networkx`: Graph data structures and algorithms
- `pandas` and `numpy`: Data processing and analysis
- `openpyxl`: Excel file processing
- Azure SDK components for the chatbot interface

See `requirements.txt` for a complete list of dependencies.