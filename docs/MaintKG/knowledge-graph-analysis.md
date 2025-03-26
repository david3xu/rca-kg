# Knowledge Graph Implementation for Root Cause Analysis

## Knowledge Graph Structure and Design Principles

MaintKG implements a domain-specific knowledge graph optimized for maintenance analytics with three primary node categories:

1. **System Nodes**: Represent physical equipment hierarchies
   ```cypher
   (:System {name: "Pump-XJ42", location: "Plant-North"})
   ```

2. **Record Nodes**: Capture maintenance work orders with temporal and contextual metadata
   ```cypher
   (:Record {id: "WO-10234", date: "2022-05-17", type: "unplanned", cost: 2500})
   ```

3. **Entity Nodes**: Represent domain concepts with hierarchical typing
   ```cypher
   (:Object:Component {name: "bearing"})
   (:Activity:Maintenance {name: "replace"})
   (:State:Condition {name: "leaking"})
   ```

These nodes are connected through semantically typed relationships that form the analytical backbone:

```cypher
(s:System)-[:HAS_RECORD]->(r:Record)
(r:Record)-[:MENTIONS]->(e:Entity)
(e1:Entity)-[:HAS_PART|CONTAINS|HAS_PROPERTY|HAS_PATIENT]->(e2:Entity)
```

## Statistical Significance Through PMI Integration

A critical feature of MaintKG's implementation is the quantification of relationship significance through PMI (Pointwise Mutual Information) scores:

```cypher
// Relationship with PMI score indicating statistical significance
(a:Activity {name: "replace"})-[:HAS_PATIENT {pmi: 0.82, frequency: 24}]->(o:Object {name: "bearing"})
```

PMI values enable algorithmic prioritization of potential causal factors by quantifying how much more frequently entities co-occur in relationships than would be expected by chance:

```
PMI(x,y) = log( P(x,y) / (P(x) * P(y)) )
```

Where:
- P(x,y) is the probability of entities x and y occurring together
- P(x) and P(y) are the individual probabilities of entities x and y

This statistical foundation transforms subjective maintenance observations into objective, data-driven insights.

## Root Cause Analysis Implementation

The knowledge graph architecture enables sophisticated root cause analysis through multi-dimensional traversal and pattern recognition.

### Use Case: Recurring Bearing Failures

Consider a scenario where multiple pump bearing failures have been recorded. Identifying the root cause requires traversing the knowledge graph along multiple analytical dimensions:

#### Step 1: Identify the Failure Pattern

```cypher
// Find systems with multiple bearing failures
MATCH (s:System)-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(o:Object)
WHERE o.name = 'bearing' AND r.type = 'unplanned'
WITH s.name AS SystemName, COUNT(DISTINCT r) AS FailureCount
WHERE FailureCount > 3
RETURN SystemName, FailureCount
ORDER BY FailureCount DESC
```

This query might identify "Pump-XJ42" with 7 bearing failures over the past year.

#### Step 2: Temporal Failure Analysis

```cypher
// Find time between failures for the specific system
MATCH (s:System {name: 'Pump-XJ42'})-[:HAS_RECORD]->(r:Record)-[:MENTIONS]->(o:Object {name: 'bearing'})
WHERE r.type = 'unplanned'
WITH r ORDER BY r.date
WITH COLLECT(r.date) AS FailureDates,
     [i IN RANGE(0, SIZE(COLLECT(r))-2) | 
      DURATION.BETWEEN(COLLECT(r)[i].date, COLLECT(r)[i+1].date).days] AS TimeBetweenFailures
RETURN FailureDates, TimeBetweenFailures, AVG(TimeBetweenFailures) AS AverageDaysBetweenFailures
```

This reveals that failures occur approximately every 45 days.

#### Step 3: Identify Potential Causal Factors

```cypher
// Find entities commonly mentioned before bearing failures
MATCH (bearing:Object {name: 'bearing'})<-[:MENTIONS]-(r1:Record)-[:HAS_RECORD]->(s:System {name: 'Pump-XJ42'}),
      (candidate:Entity)<-[:MENTIONS]-(r2:Record)-[:HAS_RECORD]->(s)
WHERE r2.date < r1.date 
      AND r2.date > r1.date - duration('P14D')  // Within 14 days before failure
      AND candidate.name <> bearing.name
WITH candidate.name AS PotentialCause, candidate.type AS CauseType, COUNT(DISTINCT r1) AS Occurrences
WHERE Occurrences > 2
RETURN PotentialCause, CauseType, Occurrences
ORDER BY Occurrences DESC
```

This query might reveal that "vibration" (State) appears in 5 out of 7 reports preceding bearing failures.

#### Step 4: Analyze Semantic Relationships

```cypher
// Find strong semantic relationships involving the symptom
MATCH (vibration:State {name: 'vibration'})<-[r1]-(e:Entity)-[r2]->(bearing:Object {name: 'bearing'})
WHERE r1.pmi > 0.6 AND r2.pmi > 0.6
RETURN e.name AS IntermediaryFactor, e.type AS FactorType, 
       TYPE(r1) AS RelationToSymptom, TYPE(r2) AS RelationToFailure,
       r1.pmi AS ConfidenceSymptom, r2.pmi AS ConfidenceFailure
```

This might reveal that "misalignment" (State) has strong semantic connections to both vibration and bearing failure.

#### Step 5: Validate Root Cause Hypothesis

```cypher
// Validate maintenance effectiveness for addressing root cause
MATCH (s:System {name: 'Pump-XJ42'})-[:HAS_RECORD]->(r1:Record)-[:MENTIONS]->(align:Activity {name: 'align'}),
      (s)-[:HAS_RECORD]->(r2:Record)-[:MENTIONS]->(bearing:Object {name: 'bearing'})
WHERE r2.date > r1.date
WITH r1, COLLECT(r2) AS SubsequentFailures
WITH r1.date AS MaintenanceDate, 
     SIZE(SubsequentFailures) AS FailuresAfterMaintenance,
     CASE WHEN SIZE(SubsequentFailures) > 0 
          THEN MIN([f in SubsequentFailures | f.date]) 
          ELSE NULL END AS NextFailureDate
RETURN MaintenanceDate, 
       FailuresAfterMaintenance,
       NextFailureDate,
       CASE WHEN NextFailureDate IS NOT NULL 
            THEN DURATION.BETWEEN(MaintenanceDate, NextFailureDate).days 
            ELSE NULL END AS DaysUntilNextFailure
```

This analysis might reveal that after alignment maintenance, the time until the next bearing failure extended significantly, validating misalignment as a root cause.

## Knowledge Graph Implementation Advantages

MaintKG's knowledge graph approach provides several key advantages for root cause analysis:

1. **Multi-dimensional Analysis**: Enables simultaneous traversal across equipment components, time periods, and causal factors to identify non-obvious correlations

2. **Integrated Heterogeneous Data**: Unifies temporal, causal, and physical information that would otherwise remain fragmented across separate maintenance records

3. **Statistical Significance**: PMI scores provide an objective basis for prioritizing potential causes, focusing attention on statistically significant relationships

4. **Causal Chain Discovery**: Supports the identification of causal pathways through equipment systems and subsystems, revealing hidden dependencies

5. **Temporal Pattern Recognition**: Facilitates the discovery of recurring failure patterns and maintenance effectiveness through time-based analysis

6. **Iterative Knowledge Enhancement**: Each new maintenance record potentially reinforces existing relationships or introduces new entities and connections, creating a continuously evolving knowledge repository

## Implementation Considerations

Effective root cause analysis through knowledge graphs requires attention to several implementation details:

1. **Ontological Design**: The entity type hierarchy must balance specificity (detailed component types) with generality (broad semantic categories) to enable flexible querying

2. **Relationship Constraints**: Domain-specific constraints on relationship types ensure semantic coherence while enabling comprehensive analysis

3. **Temporal Modeling**: Effective representation of time-based relationships is essential for causal analysis across maintenance events

4. **Statistical Thresholds**: Setting appropriate PMI thresholds requires balancing precision (high confidence) with recall (comprehensive coverage)

5. **Query Optimization**: Complex traversal patterns require efficient indexing and query optimization to maintain interactive performance

## Conclusion

MaintKG's knowledge graph implementation provides a powerful framework for maintenance root cause analysis by integrating multi-dimensional information into a unified representation. Through its combination of semantic typing, statistical significance measures, and temporal relationships, it enables sophisticated causal analysis that would be impossible with traditional database approaches.

By traversing the knowledge graph along physical, semantic, and temporal dimensions, maintenance analysts can identify root causes of equipment failures, predict potential issues before they occur, and optimize maintenance strategies to minimize downtime and maintenance costs.
