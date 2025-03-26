# Knowledge Graph Queries for Maintenance Root Cause Analysis

## Graph Structure and Query Foundation

MaintKG implements a domain-specific graph structure optimized for maintenance analytics, with three primary node types:

1. **System Nodes**: Represent physical assets or equipment hierarchies
2. **Record Nodes**: Capture maintenance work orders with temporal and contextual metadata
3. **Entity Nodes**: Encode domain concepts with hierarchical typing (objects, activities, states, processes)

These nodes form an interconnected network through semantically typed relationships:

```
(System)-[HAS_RECORD]->(Record)-[MENTIONS]->(Entity)
(Entity)-[HAS_PART|CONTAINS|HAS_PROPERTY|HAS_PATIENT]->(Entity)
```

## Neo4j Cypher Query Implementation

MaintKG leverages Neo4j's Cypher query language to enable complex pattern matching across the knowledge graph. Each query consists of three key components:

1. **Pattern Specification**: Defines the node and relationship patterns to match
2. **Filtering Conditions**: Constrains results based on property values
3. **Result Projection**: Transforms matched patterns into the desired output format

Example query to identify systems with bearing failures:

```cypher
MATCH (s:System)-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(e:Object)
WHERE e.name CONTAINS 'bearing' AND r.type = 'unplanned'
RETURN s.name AS SystemName, COUNT(DISTINCT r) AS FailureCount
ORDER BY FailureCount DESC
```

## Root Cause Analysis Query Patterns

MaintKG supports several advanced query patterns for root cause analysis:

### Component Failure Propagation Analysis

Identifies how failures in one component correlate with subsequent failures in connected components:

```cypher
MATCH (primary:Object)<-[:MENTIONS]-(r1:Record)-[:HAS_RECORD]-(s:System),
      (secondary:Object)<-[:MENTIONS]-(r2:Record)-[:HAS_RECORD]-(s)
WHERE primary.name = 'bearing' AND r1.date < r2.date 
      AND r2.date < r1.date + duration('P30D')
WITH secondary.name AS SecondaryFailure, COUNT(*) AS Occurrences
WHERE Occurrences > 5
RETURN SecondaryFailure, Occurrences
ORDER BY Occurrences DESC
```

### Statistical Relevance Filtering

Utilizes PMI (Pointwise Mutual Information) scores to identify statistically significant relationships:

```cypher
MATCH (a:Activity)-[r:HAS_PATIENT]->(o:Object)
WHERE r.pmi > 0.75
RETURN a.name AS Maintenance_Activity, o.name AS Target_Component, 
       r.pmi AS Confidence
ORDER BY r.pmi DESC
LIMIT 10
```

### Temporal Pattern Analysis

Detects recurring failures and maintenance effectiveness through time-based queries:

```cypher
MATCH (s:System)-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(e:Object)
WHERE e.name = 'pump' AND r.type = 'unplanned'
WITH s, r ORDER BY r.date
WITH s.name AS SystemName, COLLECT(r.date) AS FailureDates,
     [i IN RANGE(0, SIZE(COLLECT(r))-2) | 
      DURATION.BETWEEN(COLLECT(r)[i].date, COLLECT(r)[i+1].date).days] 
      AS TimeBetweenFailures
WHERE SIZE(FailureDates) > 3
RETURN SystemName, FailureDates, TimeBetweenFailures, 
       AVG(TimeBetweenFailures) AS AverageDaysBetweenFailures
ORDER BY AverageDaysBetweenFailures
```

## Implementing Complex Root Cause Queries

For advanced root cause analysis, MaintKG combines multiple query techniques:

```cypher
// Find potential root causes for repeated bearing failures
MATCH (bearing:Object {name: 'bearing'})<-[:MENTIONS]-(r1:Record)-[:HAS_RECORD]->(s:System),
      (potentialCause:Object)<-[:MENTIONS]-(r2:Record)-[:HAS_RECORD]->(s)
WHERE r2.date < r1.date AND bearing.name <> potentialCause.name
WITH potentialCause, COUNT(DISTINCT r1) AS FailureCount
WHERE FailureCount > 3
RETURN potentialCause.name AS PotentialRootCause, 
       FailureCount AS RelatedBearingFailures
ORDER BY FailureCount DESC
```

This query pattern:
1. Identifies bearing failure records
2. Locates preceding maintenance records for the same system
3. Extracts components mentioned in those records
4. Counts frequency of co-occurrence
5. Ranks potential causal factors

## Query Execution and Performance Optimization

Effective implementation of root cause analysis queries requires several performance considerations:

1. **Index Utilization**: Creating indices on frequently queried properties (names, dates, types)
2. **Query Profiling**: Analyzing execution plans to identify bottlenecks
3. **Parameter Usage**: Implementing parameterized queries for repeated execution
4. **Result Limiting**: Constraining result sets for complex pattern matches
5. **Aggregation Strategies**: Using efficient aggregation functions for statistical analysis

## Extension to Predictive Maintenance

The query patterns can be extended to support predictive maintenance:

```cypher
// Predict potential failures based on historic patterns
MATCH (symptom:State)<-[:MENTIONS]-(r1:Record)-[:HAS_RECORD]->(s1:System),
      (failure:Object)<-[:MENTIONS]-(r2:Record)-[:HAS_RECORD]->(s1)
WHERE r1.date < r2.date AND r2.date < r1.date + duration('P14D')
WITH symptom, failure, COUNT(*) AS PatternCount
WHERE PatternCount > 3
MATCH (s2:System)-[:HAS_RECORD]->(r3:Record)-[:MENTIONS]->(symptom)
WHERE NOT EXISTS {
  MATCH (s2)-[:HAS_RECORD]->(r4:Record)-[:MENTIONS]->(failure)
  WHERE r3.date < r4.date AND r4.date < r3.date + duration('P14D')
}
RETURN s2.name AS AtRiskSystem, symptom.name AS ObservedSymptom,
       failure.name AS PredictedFailure, r3.date AS SymptomDate,
       PatternCount AS HistoricalOccurrences
```

This query identifies systems exhibiting symptoms that have historically preceded specific failures, enabling proactive maintenance interventions.

Through these structured query patterns, MaintKG transforms maintenance records into actionable insights for failure prevention and operational optimization.
