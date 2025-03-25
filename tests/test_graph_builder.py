#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test cases for knowledge graph builder.
"""

import unittest
import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder


class TestKnowledgeGraphBuilder(unittest.TestCase):
    """Test cases for the KnowledgeGraphBuilder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent / "test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Create test relationships
        self.test_relationships = [
            {"source": "A", "target": "B", "type": "causes", "strength": 0.8},
            {"source": "B", "target": "C", "type": "causes", "strength": 0.6},
            {"source": "A", "target": "C", "type": "correlates", "strength": 0.5},
            {"source": "D", "target": "B", "type": "influences", "strength": 0.7}
        ]
        
        # Save test relationships to file
        with open(self.test_data_dir / "test_relationships.json", "w") as f:
            json.dump(self.test_relationships, f)
        
        # Initialize builder with test config
        self.test_config = {
            "data_dir": str(self.test_data_dir),
            "output_dir": str(self.test_data_dir)
        }
        
        # Create test config file
        with open(self.test_data_dir / "test_config.json", "w") as f:
            json.dump(self.test_config, f)
        
        self.builder = KnowledgeGraphBuilder(self.test_data_dir / "test_config.json")
    
    def test_build_graph(self):
        """Test building a graph from relationships."""
        graph = self.builder.build_graph(self.test_relationships)
        
        # Check nodes
        self.assertEqual(len(graph.nodes), 4)
        self.assertIn("A", graph.nodes)
        self.assertIn("B", graph.nodes)
        self.assertIn("C", graph.nodes)
        self.assertIn("D", graph.nodes)
        
        # Check edges
        self.assertEqual(len(graph.edges), 4)
        self.assertIn(("A", "B"), graph.edges)
        self.assertIn(("B", "C"), graph.edges)
        self.assertIn(("A", "C"), graph.edges)
        self.assertIn(("D", "B"), graph.edges)
        
        # Check edge attributes
        self.assertEqual(graph["A"]["B"]["type"], "causes")
        self.assertEqual(graph["A"]["B"]["strength"], 0.8)
    
    def test_analyze_graph(self):
        """Test analyzing a graph."""
        self.builder.build_graph(self.test_relationships)
        analysis = self.builder.analyze_graph()
        
        # Check that analysis contains expected keys
        self.assertIn("degree_centrality", analysis)
        self.assertIn("in_degree_centrality", analysis)
        self.assertIn("out_degree_centrality", analysis)
        self.assertIn("betweenness_centrality", analysis)
        self.assertIn("root_cause_candidates", analysis)
        
        # Check root cause candidates
        self.assertIn("A", analysis["root_cause_candidates"])
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test files in the real implementation
        pass


if __name__ == "__main__":
    unittest.main() 