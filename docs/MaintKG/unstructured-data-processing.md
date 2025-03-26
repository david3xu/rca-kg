# Unstructured Data Processing in MaintKG

## Overview of Text Processing Pipeline

MaintKG implements a sophisticated multi-stage pipeline for transforming unstructured maintenance work order text into structured knowledge graph representations. This process addresses the fundamental challenge of converting domain-specific technical language into machine-interpretable semantic knowledge.

## 1. Text Preprocessing and Normalization

The initial stage prepares raw maintenance text through systematic transformations to ensure consistency and improve extraction quality:

```python
def simple_preprocessing(text: str, non_semantic_codes: Optional[List[str]] = None) -> str:
    # Remove facility-specific codes without semantic value
    if non_semantic_codes:
        regex_pattern = r"\b(" + "|".join(map(re.escape, non_semantic_codes)) + r")\b"
        t = re.sub(regex_pattern, " ", text, flags=re.IGNORECASE)
    
    # Preserve technical characters while cleaning text
    chars_to_preserve = [",", "&", ".", "#", "@", "/", "-", "[", "]", "(", ")"]
    t = preserve_chars(t, chars_to_preserve=chars_to_preserve)
    
    # Standardize technical terminology
    t = correct_typos(text=t, corrections_dict=corrections_dict)
    
    # Replace identifiers and numerical values
    t = re.sub(r"\b(?=\w*[a-zA-Z])(?=\w*\d)\w+\b", " ", t)
    t = re.sub(r"\b\d+\b", " <num> ", t)
    
    # Normalize formatting and punctuation
    # [additional normalization steps...]
    
    return re.sub("\s+", " ", t).strip()
```

Key normalization operations include:

- **Code Filtering**: Removing non-semantic organization-specific codes
- **Character Preservation**: Maintaining domain-specific notation and symbols
- **Terminology Standardization**: Applying correction dictionaries for technical terms
- **Token Normalization**: Replacing alphanumeric identifiers and numerical values
- **Format Standardization**: Normalizing whitespace and punctuation

This preprocessing ensures consistent input for the semantic extraction model while preserving maintenance-specific terminology.

## 2. Deep Learning-Based Information Extraction

The core extraction is performed by NoisIE (Normalization and Information Extraction), a sequence-to-sequence model based on the ByT5 architecture:

```python
class NoisIE:
    def inference(self, data: List[str]) -> List[InferenceOutput]:
        """Process batches of text and generate structured output."""
        dataloader = self.prepare_dataset(data)
        outputs = []
        
        for batch_idx, batch in enumerate(dataloader):
            batch = {k: v.to(self.device) for k, v in batch.items()}
            inputs, preds = self.model.generate_samples(batch)
            
            for input_text, prediction in zip(inputs, preds):
                output = self._process_single_output(
                    input_text=input_text,
                    prediction=prediction,
                    batch_idx=batch_idx,
                    item_idx=len(outputs)
                )
                outputs.append(output)
                
        return outputs
```

The model processes batches of preprocessed text and generates structured outputs containing:

1. **Normalizations**: Mappings between surface forms and canonical forms
2. **Entities**: Domain objects with their semantic types
3. **Relations**: Semantic connections between entities

## 3. Semantic Structure Parsing

The model output is parsed into a structured format through pattern recognition:

```python
def structure_noisie_string(input_str: str, noisie_str: str):
    """Parse structured output from NoisIE model."""
    # Categorize output sections
    text_sections = parse_and_categorize_sections(noisie_str)
    text_spans = text_sections["spans"]
    text_tokens = text_sections["tokens"]
    
    data = {
        "norms": [],
        "entities": [],
        "relations": [],
        "issues": {"norms": {}, "entities": {}, "relations": {}, "general": {}}
    }
    
    # Process each category of spans
    for cat, spans in text_spans.items():
        for start, end in spans:
            span_tokens = tuple(text_tokens[start : end + 1])
            
            if cat == "norm":
                # Extract normalization pairs
                norm_string = " ".join(text_tokens[start : end + 1])
                norm_parts = parse_abbreviation_full_form(norm_string)
                data["norms"] = norm_parts
            elif cat == "relation":
                # Extract relation assertions
                ie_item = tuple(text_tokens[start : end + 1])
                data["relations"].append(process_triple(ie_item))
            elif cat == "entity":
                # Extract entity mentions
                data["entities"].append(span_tokens)
    
    # Validate and sanitize output components
    for key in ["norms", "entities", "relations"]:
        # Validation logic for each component type...
    
    return data
```

This function analyzes the linearized model output and extracts:

- **Normalization pairs**: `<norm> guage [ gauge ]` → `("guage", "gauge")`
- **Entity spans**: `<entity> service <activity>` → `("service", "activity")`
- **Relation assertions**: `<relation> faulty <state> gauge <object> has patient` → `("gauge", "object", "faulty", "state", "has_patient")`

## 4. Triple Validation and Refinement

Extracted semantic triples undergo multiple validation stages:

```python
def validate_triple(triple: Tuple[str, str, str, str, str]) -> Tuple[bool, str]:
    """Validate a triple against semantic constraints."""
    head, head_type, tail, tail_type, relation = triple
    
    # Check for self-references
    if head == tail and head_type == tail_type:
        return False, "self-reference"
    
    # Verify entity surface forms
    if head == "" or tail == "":
        return False, "empty entity surface form"
    
    # Validate entity types against ontology
    if (head_type.split("/")[0] not in ENTITY_TYPES or 
        tail_type.split("/")[0] not in ENTITY_TYPES):
        return False, "invalid entity type(s)"
    
    # Validate relation types
    if relation not in RELATION_TYPES:
        return False, "invalid relation type"
    
    # Check entity-relation-entity pattern validity
    if (head_type.split("/")[0], tail_type.split("/")[0]) not in RELATION_CONSTRAINTS.get(relation):
        return False, "invalid triple pattern"
    
    return True, "valid"
```

Validation rules ensure:
- No self-referential triples (same entity as head and tail)
- Entity types conform to the maintenance domain ontology
- Relations follow domain-specific constraints
- Triple patterns adhere to predefined semantic rules

## 5. Semantic Enhancement

Valid triples undergo semantic enhancement through:

```python
def process_node(node: Node, use_gazetteer: bool = False) -> Tuple[Node, List[str], bool]:
    """Enhance entity nodes with normalization and type refinement."""
    # Normalize node surface form
    new_name, norm_ops, name_changed = normalise(s=node.name, tag=node.type)
    if name_changed:
        node.name = new_name
    
    # Apply gazetteer-based type enhancement
    if use_gazetteer:
        gazetteer_mapping = gazetteer.get(node.type)
        if gazetteer_mapping is not None:
            hierarchy = gazetteer_mapping.get(node.name, node.type)
            node.type = hierarchy
    
    return node, norm_ops, name_changed
```

Enhancement includes:
- **Surface form normalization**: Standardizing terminology variants
- **Lemmatization**: Applying part-of-speech specific normalization based on entity type
- **Fine-grained typing**: Using a domain gazetteer to assign more specific entity types
- **Statistical enrichment**: Calculating PMI for relationship strength measurement

## 6. PMI Calculation for Statistical Significance

A distinguishing feature of MaintKG is the calculation of Pointwise Mutual Information (PMI) to measure the statistical significance of extracted relationships:

```python
def calculate_pmi(triple: Triple, triple_prob: dict, head_prob: dict, 
                 relation_prob: dict, tail_prob: dict) -> float:
    """Calculate PMI score for a triple."""
    p_ijk = triple_prob[(triple.head.name, triple.relation.name, triple.tail.name)]
    p_i = head_prob[triple.head.name]
    p_k = relation_prob[triple.relation.name]
    p_j = tail_prob[triple.tail.name]
    return math.log(p_ijk / (p_i * p_k * p_j))
```

PMI quantifies how much more frequently entities co-occur in a relationship than would be expected by chance, providing an objective measure of relationship significance.

## 7. Knowledge Graph Integration

The refined semantic triples are integrated into the Neo4j knowledge graph:

```python
def _create_db_triple(self: Self, session: Session, triple: Triple) -> Any:
    """Create a triple in the Neo4J database."""
    # Create or update head entity node
    head_node = session.execute_write(
        create_or_get_node,
        triple.head.name,
        triple.head.type,
        triple.head.properties,
        {self.settings.processing.start_date_col},
    )
    
    # Create or update tail entity node
    tail_node = session.execute_write(
        create_or_get_node,
        triple.tail.name,
        triple.tail.type,
        triple.tail.properties,
        {self.settings.processing.start_date_col},
    )
    
    # Establish typed relationship between nodes
    return session.execute_write(
        create_relationship,
        head_node,
        triple.relation.name,
        tail_node,
        triple.relation.properties,
    )
```

## 8. Statistical Filtering for Quality Assurance

A final filtering stage removes statistical outliers:

```python
remove_triple = (_stat_triple.relation.properties["frequency"] == 1) and (
    (_stat_triple.relation.properties["pmi"] < self.pmi_lower) or 
    (self.pmi_upper < _stat_triple.relation.properties["pmi"])
)
```

This threshold-based filtering ensures:
- Removal of statistically improbable relationships
- Retention of meaningful domain-specific correlations
- Balanced precision and recall in the knowledge representation

Through this comprehensive pipeline, MaintKG transforms unstructured maintenance descriptions into a structured, queryable knowledge graph that enables sophisticated root cause analysis and maintenance optimization.
