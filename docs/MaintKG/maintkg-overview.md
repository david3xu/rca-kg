# MaintKG: Automated Maintenance Knowledge Graph Framework

## Overview and Architecture

MaintKG is a specialized framework designed to transform unstructured maintenance work order records into structured, graph-based knowledge representations. Developed by the UWA NLP-TLP Team, this system enables advanced maintenance analytics through semantic reasoning and pattern recognition techniques.

## Core Components and Processing Pipeline

The framework implements a multi-stage processing pipeline that systematically converts raw maintenance text into a queryable knowledge graph:

### 1. Data Preparation
- **Input Processing**: Ingests CMMS (Computerized Maintenance Management System) records
- **Metadata Extraction**: Captures contextual information about maintenance events, including dates, costs, and system identifiers
- **Record Classification**: Categorizes work orders as planned/unplanned maintenance activities

### 2. Information Extraction (NoisIE)
- **Sequence-to-Sequence Transformation**: Implements a specialized deep learning model for maintenance text processing
- **Entity Recognition**: Identifies domain-specific concepts like objects, activities, states, and processes
- **Relation Extraction**: Captures semantic connections between entities
- **Normalization**: Standardizes technical terminology and abbreviations

### 3. Knowledge Refinement
- **Triple Validation**: Enforces semantic constraints on extracted knowledge assertions
- **Entity Normalization**: Applies linguistic operations to standardize terminology
- **Type Enhancement**: Enriches entities with fine-grained semantic classifications
- **Statistical Analysis**: Calculates PMI (Pointwise Mutual Information) to quantify relationship significance

### 4. Graph Construction
- **Node Creation**: Establishes typed entity instances in the knowledge graph
- **Relationship Mapping**: Connects entities through semantic relationships
- **Property Assignment**: Enriches nodes and edges with metadata
- **Statistical Filtering**: Removes low-confidence assertions based on PMI thresholds

### 5. Neo4j Integration
- **Database Schema**: Implements a flexible, property graph model
- **Query Interface**: Enables complex pattern matching for maintenance analysis
- **Traversal Operations**: Supports multi-hop reasoning across entity relationships

## Technical Implementation

MaintKG leverages several modern technologies to achieve its knowledge extraction capabilities:

- **PyTorch & PyTorch Lightning**: Powers the NoisIE information extraction model
- **Pydantic**: Ensures robust data validation and configuration management
- **Neo4j**: Provides the graph database backend for efficient storage and querying
- **Python 3.9+**: Implements the core processing logic with type annotations

The system architecture prioritizes:
- **Modularity**: Clear separation between processing stages
- **Extensibility**: Pluggable components for customization
- **Reproducibility**: Consistent processing pipeline with configurable parameters
- **Performance**: Efficient handling of large maintenance record collections

## Practical Applications

This framework addresses several critical needs in maintenance analytics:

1. **Structured Knowledge Extraction**: Transforms unstructured text records into machine-readable knowledge
2. **Semantic Search**: Enables querying across maintenance records based on meaning rather than keywords
3. **Root Cause Analysis**: Facilitates identification of recurring issues and their interconnections
4. **Asset Relationship Mapping**: Creates a comprehensive view of maintenance activities across systems
5. **Failure Pattern Recognition**: Identifies temporal and causal patterns in maintenance events

## Implementation Process

The end-to-end process begins with raw maintenance records and produces a queryable knowledge graph:

1. **Loading Data**: Imports and normalizes maintenance records from CSV files
2. **Processing Text**: Applies linguistic preprocessing to standardize maintenance descriptions
3. **Extracting Knowledge**: Identifies entities and relationships using the NoisIE model
4. **Refining Triples**: Validates and enhances extracted knowledge assertions
5. **Building Graph**: Constructs Neo4j database with optimized structure for querying
6. **Analyzing Patterns**: Performs root cause analysis through graph traversal operations

MaintKG strikes a balance between automated processing and statistical filtering, ensuring that the resulting knowledge graph contains high-confidence information while filtering out noise and low-value assertions.
