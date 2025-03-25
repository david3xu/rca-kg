#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script to process Excel files for root cause analysis.
This script processes Excel files with hierarchical data and metadata.
"""

import argparse
import os
from pathlib import Path
import sys
import json
from excel_metadata_processor import convert_hierarchical_excel, batch_process_excel_files


def main():
    """Main entry point for Excel data processing."""
    parser = argparse.ArgumentParser(
        description='Process Excel files with hierarchical data and metadata detection'
    )
    
    # Command options
    parser.add_argument(
        '--single', '-s',
        help='Process a single Excel file',
        action='store_true'
    )
    
    parser.add_argument(
        '--batch', '-b',
        help='Process all Excel files in a directory',
        action='store_true'
    )
    
    # File/directory arguments
    parser.add_argument(
        '--input', '-i',
        help='Input Excel file or directory path',
        required=True
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file or directory path',
        required=True
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.single and not args.batch:
        parser.error("Please specify either --single or --batch mode")
    
    # Execute based on mode
    if args.single:
        if not os.path.isfile(args.input):
            parser.error(f"Input file not found: {args.input}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            print(f"Processing file: {args.input}")
            result = convert_hierarchical_excel(args.input, args.output)
            print(f"Metadata fields detected: {len(result['metadata'])}")
            print(f"Data records processed: {len(result['data'])}")
            print(f"Output saved to: {args.output}")
            
            return 0
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return 1
    
    elif args.batch:
        if not os.path.isdir(args.input):
            parser.error(f"Input directory not found: {args.input}")
        
        # Ensure output directory exists
        if not os.path.exists(args.output):
            os.makedirs(args.output, exist_ok=True)
        
        try:
            print(f"Processing all Excel files in: {args.input}")
            results = batch_process_excel_files(args.input, args.output)
            
            # Print summary
            success_count = sum(1 for r in results.values() if r.get('status') == 'success')
            error_count = sum(1 for r in results.values() if r.get('status') == 'error')
            
            print("\nProcessing Summary:")
            print(f"Total files: {len(results)}")
            print(f"Successfully processed: {success_count}")
            print(f"Errors: {error_count}")
            print(f"Detailed summary saved to: {os.path.join(args.output, 'processing_summary.json')}")
            
            return 0 if error_count == 0 else 1
        except Exception as e:
            print(f"Error in batch processing: {str(e)}")
            return 1


if __name__ == "__main__":
    sys.exit(main()) 