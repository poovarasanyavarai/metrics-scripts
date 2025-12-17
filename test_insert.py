#!/usr/bin/env python3
"""
Simple script to test database insertion
"""
from db_calls import insert_metrics_to_db
import os

if __name__ == "__main__":
    # Find the latest JSON file
    json_files = [f for f in os.listdir('.') if f.startswith('chatbot_metrics_insert_format_') and f.endswith('.json')]
    if not json_files:
        print("No JSON files found")
        exit(1)

    latest_file = sorted(json_files)[-1]
    print(f"Testing insertion with file: {latest_file}")

    if insert_metrics_to_db(latest_file):
        print("✅ Insertion successful!")
    else:
        print("❌ Insertion failed!")