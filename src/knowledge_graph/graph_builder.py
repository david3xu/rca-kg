#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge Graph Builder for Root Cause Analysis.
This module constructs the knowledge graph from processed data.
"""

import networkx as nx
import json
import matplotlib.pyplot as plt
from pathlib import Path
import os


class KnowledgeGraphBuilder:
    """Build and analyze knowledge graphs for root cause analysis."""
    
    def __init__(self, config_path=None):
        """Initialize with optional configuration file."""
        self.config = {}
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Default configuration
        self.data_dir = self.config.get('data_dir', 
                                       '../../../data/processed')
        self.output_dir = self.config.get('output_dir',
                                         '../../../data/knowledge_graph')
        self.graph = nx.DiGraph()
    
    def load_relationships(self, filename):
        """Load relationship data from processed files."""
        file_path = Path(self.data_dir) / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def build_graph(self, relationships):
        """Build the knowledge graph from relationships."""
        for rel in relationships:
            source = rel['source']
            target = rel['target']
            
            # Add nodes if they don't exist
            if source not in self.graph:
                self.graph.add_node(source)
            if target not in self.graph:
                self.graph.add_node(target)
            
            # Add edge with properties
            self.graph.add_edge(
                source, 
                target, 
                type=rel.get('type', 'related'),
                strength=rel.get('strength', 1.0),
                metadata=rel.get('metadata', {})
            )
        
        return self.graph
    
    def analyze_graph(self):
        """Perform graph analysis for root cause identification."""
        analysis = {}
        
        # Centrality measures
        analysis['degree_centrality'] = nx.degree_centrality(self.graph)
        analysis['in_degree_centrality'] = nx.in_degree_centrality(self.graph)
        analysis['out_degree_centrality'] = nx.out_degree_centrality(self.graph)
        
        # Influence measures
        analysis['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
        
        # Community detection
        try:
            analysis['communities'] = list(nx.community.greedy_modularity_communities(
                self.graph.to_undirected()))
        except:
            # Some community detection algorithms require connected graphs
            analysis['communities'] = []
        
        # Potential root cause candidates (nodes with high out-degree)
        sorted_nodes = sorted(
            analysis['out_degree_centrality'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        analysis['root_cause_candidates'] = [
            node for node, score in sorted_nodes[:5]
        ]
        
        return analysis
    
    def visualize_graph(self, output_file='graph.png'):
        """Visualize the knowledge graph."""
        plt.figure(figsize=(12, 10))
        
        # Position nodes using force-directed layout
        pos = nx.spring_layout(self.graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, 
            pos, 
            node_size=700, 
            node_color='lightblue',
            alpha=0.8
        )
        
        # Draw edges
        edge_colors = [self.graph[u][v].get('strength', 0.5) for u, v in self.graph.edges()]
        nx.draw_networkx_edges(
            self.graph, 
            pos, 
            width=2, 
            alpha=0.5, 
            edge_color=edge_colors, 
            edge_cmap=plt.cm.Blues
        )
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10)
        
        # Save visualization
        output_path = Path(self.output_dir) / output_file
        os.makedirs(output_path.parent, exist_ok=True)
        plt.tight_layout()
        plt.axis('off')
        plt.savefig(output_path, format='png', dpi=300)
        plt.close()
        
        return output_path
    
    def export_graph(self, output_file='graph.json'):
        """Export the graph in JSON format."""
        output_path = Path(self.output_dir) / output_file
        os.makedirs(output_path.parent, exist_ok=True)
        
        # Convert NetworkX graph to dictionary
        data = nx.node_link_data(self.graph)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path


if __name__ == "__main__":
    # Example usage
    builder = KnowledgeGraphBuilder()
    # relationships = builder.load_relationships("relationships.json")
    # graph = builder.build_graph(relationships)
    # analysis = builder.analyze_graph()
    # builder.visualize_graph()
    # builder.export_graph()
    print("Knowledge graph builder ready.")
