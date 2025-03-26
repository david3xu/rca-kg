# MaintKG: Knowledge Graph Implementation for Root Cause Analysis

## Overview

MaintKG is a framework for transforming unstructured maintenance work order records into structured knowledge graphs that enable sophisticated root cause analysis. By combining natural language processing, semantic extraction, and graph-based reasoning, MaintKG creates a queryable knowledge representation that reveals hidden patterns and causal relationships in maintenance data.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Data Preparation](#data-preparation)
6. [Running the Pipeline](#running-the-pipeline)
7. [Querying the Knowledge Graph](#querying-the-knowledge-graph)
8. [Root Cause Analysis Methodology](#root-cause-analysis-methodology)
9. [Extending the Framework](#extending-the-framework)
10. [Troubleshooting](#troubleshooting)
11. [References](#references)

## Core Concepts

MaintKG implements a multi-stage processing pipeline:

1. **Data Ingestion**: Loads maintenance records from CMMS (Computerized Maintenance Management System) exports
2. **Text Preprocessing**: Standardizes terminology and normalizes maintenance descriptions
3. **Information Extraction**: Employs the NoisIE model to extract entities and relationships
4. **Knowledge Refinement**: Validates and enhances semantic triples with domain knowledge
5. **Graph Construction**: Transforms refined triples into a Neo4j knowledge graph
6. **Query Interface**: Enables pattern-based analysis through Cypher queries

The resulting knowledge graph represents:
- Physical systems and components (pumps, bearings, seals)
- Operational states and conditions (leaking, vibration, misalignment)
- Maintenance activities (replace, repair, inspect)
- Semantic relationships (has_part, causes, affects)
- Temporal sequences (before, after, during)

## System Requirements

- **Python 3.9+**
- **PyTorch** (CUDA-enabled recommended for NoisIE model)
- **Neo4j** Database Server (v4.4+)
- **8GB RAM** (minimum), **16GB** recommended
- **10GB** disk space for model checkpoints and intermediate data

## Installation Guide

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nl-tlp/maintkg.git
   cd maintkg
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   pip install -e .
   pip install -r requirements.txt
   ```

3. **Download NoisIE Model Checkpoint**
   ```bash
   python ./src/noisie/download_checkpoint.py
   ```

4. **Set Up Neo4j Database**
   - Install Neo4j Desktop from https://neo4j.com/download/
   - Create a new database with the following settings:
     - Name: maintkg
     - Password: Configure in `.env` file
     - Version: 4.4+
   - Start the database

## Configuration

Configure MaintKG by editing the `.env` file in the project root:

```plaintext
# Input Settings
INPUT__CSV_FILENAME='your_maintenance_data.csv'
INPUT__ID_COL='work_order_id'
INPUT__TYPE_COL='order_type'
INPUT__TEXT_COL='description'
INPUT__FLOC_COL='functional_location'
INPUT__START_DATE_COL='creation_date'
INPUT__COST_COL='total_cost'
INPUT__TIME_COL='hours_spent'
INPUT__DATE_FORMAT='%Y-%m-%d'

# Processing Settings
PROCESSING__SYSTEMS=['PUMP', 'MOTOR']  # Optional filter for specific systems
PROCESSING__UNPLANNED_ONLY=false
PROCESSING__USE_GAZETTEER=true
PROCESSING__REMOVE_SUBSUMPTION=true

# Neo4j Settings
NEO4J__URI='bolt://localhost:7687'
NEO4J__USERNAME='neo4j'
NEO4J__PASSWORD='your_password'
NEO4J__DATABASE='neo4j'

# Development Settings
DEV__DEV=false
DEV__LIMIT=1000  # Process only the first N records (for testing)
```

## Data Preparation

1. **Format Your Input Data**
   - Prepare a CSV file with maintenance records
   - Ensure required columns are present (ID, type, description, functional location)
   - Place the CSV in the `./input/` directory

2. **Non-Semantic Codes** (Optional)
   - Create a list of organization-specific codes to be filtered
   - Add to the `.env` file as:
     ```
     INPUT__NON_SEMANTIC_CODES=['CODE1', 'CODE2', 'CODE3']
     ```

3. **Work Order Type Classification**
   - Define which type codes represent planned vs. unplanned maintenance
   - Add to the `.env` file as:
     ```
     INPUT__PLANNED_TYPE_CODES=['PM', 'PREV']
     INPUT__UNPLANNED_TYPE_CODES=['CM', 'EMER', 'BRKDN']
     ```

## Running the Pipeline

Execute the complete pipeline with:

```bash
python ./src/maintkg/main.py
```

This will:
1. Process the input CSV file
2. Extract semantic information using the NoisIE model
3. Refine and validate knowledge triples
4. Construct the Neo4j knowledge graph
5. Generate output files in `./output/YYYY-MM-DD_HH-MM-SS/`

The process can be monitored through console logs, displaying progress and statistics for each stage.

## Querying the Knowledge Graph

Connect to the Neo4j database to execute Cypher queries for root cause analysis:

1. **Basic System Exploration**
   ```cypher
   // Find all systems with their associated records
   MATCH (s:System)-[:HAS_RECORD]->(r:Record)
   RETURN s.name AS SystemName, COUNT(r) AS RecordCount
   ORDER BY RecordCount DESC
   ```

2. **Component Failure Analysis**
   ```cypher
   // Find components with highest failure rates
   MATCH (s:System)-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(o:Object)
   WHERE r.type = 'unplanned'
   RETURN o.name AS Component, COUNT(DISTINCT r) AS FailureCount
   ORDER BY FailureCount DESC
   LIMIT 10
   ```

3. **Root Cause Identification**
   ```cypher
   // Find potential causes for bearing failures
   MATCH (bearing:Object {name: 'bearing'})<-[:MENTIONS]-(r1:Record)-[:HAS_RECORD]->(s:System),
         (cause:Entity)<-[:MENTIONS]-(r2:Record)-[:HAS_RECORD]->(s)
   WHERE r2.date < r1.date AND r2.date > r1.date - duration('P14D')
   WITH cause, COUNT(DISTINCT r1) AS FailureCount
   WHERE FailureCount > 3
   RETURN cause.name AS PotentialCause, cause.type AS CauseType, 
          FailureCount AS RelatedFailures
   ORDER BY FailureCount DESC
   ```

4. **Temporal Pattern Analysis**
   ```cypher
   // Analyze time between failures
   MATCH (s:System {name: 'Pump-XJ42'})-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(o:Object {name: 'bearing'})
   WHERE r.type = 'unplanned'
   WITH r ORDER BY r.date
   WITH COLLECT(r.date) AS FailureDates,
        [i IN RANGE(0, SIZE(COLLECT(r))-2) | 
         DURATION.BETWEEN(COLLECT(r)[i].date, COLLECT(r)[i+1].date).days] AS TimeBetweenFailures
   RETURN AVG(TimeBetweenFailures) AS AverageDaysBetweenFailures,
          MIN(TimeBetweenFailures) AS MinDays,
          MAX(TimeBetweenFailures) AS MaxDays
   ```

## Root Cause Analysis Methodology

Follow this systematic approach to identify root causes:

1. **Identify the Target System**
   - Select the system with recurring failures or high maintenance costs
   - Verify sufficient data records exist for meaningful analysis

2. **Analyze Failure Patterns**
   - Identify frequently failing components
   - Detect temporal patterns (seasonal, cyclical, trend-based)
   - Map failure propagation across component relationships

3. **Establish Causal Chains**
   - Use statistical relevance (PMI scores) to prioritize potential causes
   - Follow semantic relationships to identify precursor conditions
   - Trace causal paths through physical component connections

4. **Validate Hypotheses**
   - Examine maintenance interventions and their effectiveness
   - Compare time-to-failure before and after specific maintenance
   - Cross-reference findings with domain knowledge

5. **Formulate Recommendations**
   - Identify appropriate preventive maintenance strategies
   - Determine optimal maintenance intervals
   - Specify monitoring requirements for early detection

## Extending the Framework

MaintKG can be extended in several ways:

1. **Custom Entity Types**
   - Add domain-specific entity types to `resources.py`
   - Define relationship constraints for new entity types
   - Create type-specific normalization rules

2. **Enhanced Gazetteer**
   - Expand `gazetteer.json` with domain-specific terminology
   - Add fine-grained type hierarchies for industry-specific components
   - Include synonyms and variant forms for improved normalization

3. **Custom NoisIE Model**
   - Train on domain-specific maintenance corpus
   - Adjust extraction parameters for specific maintenance domains
   - Fine-tune for specialized terminology

4. **Advanced Visualization**
   - Implement custom Neo4j graph projections
   - Create domain-specific dashboard templates
   - Develop interactive analysis tools

## Troubleshooting

| Issue | Probable Cause | Solution |
|-------|---------------|----------|
| NoisIE model fails to load | Missing checkpoint files | Run `python ./src/noisie/download_checkpoint.py` |
| Low entity extraction rate | Non-standard terminology | Expand correction dictionaries in `resources.py` |
| Neo4j connection errors | Database not running or wrong credentials | Verify Neo4j is running and check credentials in `.env` |
| Out of memory errors | Large input dataset | Set `DEV__LIMIT` to process smaller batches |
| Empty knowledge graph | Invalid input data format | Check CSV column mappings in `.env` |
| Poor PMI thresholds | Insufficient data for statistical significance | Increase dataset size or adjust thresholds manually |

## References

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [MaintNormIE Dataset Access](mailto:tyler.bikaun@research.uwa.edu.au)
- [Australian Research Centre for Transforming Maintenance](https://www.maintenance.org.au/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, support, or collaboration:
- **Email**: tyler.bikaun@research.uwa.edu.au
- **GitHub Issues**: [https://github.com/nl-tlp/maintkg/issues](https://github.com/nl-tlp/maintkg/issues)
