#!/usr/bin/env python3
"""
Helper script to add new data points to the kappa report data.
This demonstrates how easy it is to update the data when new measurements
come in.
"""

import json


def add_new_data_point(date, kappa, lambda_val, data_file="data.json"):
    """
    Add a new data point to the existing data file.
    
    Args:
        date: Date string in YYYY-MM-DD format
        kappa: Kappa light chain value
        lambda_val: Lambda light chain value
        data_file: Path to the data JSON file
    """
    # Load existing data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Add new data point
    new_measurement = {
        "date": date,
        "kappa": kappa,
        "lambda": lambda_val
    }
    data["measurements"].append(new_measurement)
    
    # Save updated data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    msg = f"Added new data point: {date}, Kappa: {kappa}, Lambda: {lambda_val}"
    print(msg)


def main():
    """Example of how to add new data points."""
    print("Example: Adding new data points to the kappa report")
    print("=" * 50)
    
    # Show current data structure
    print("\nNew data structure - each measurement is a single entry:")
    print("""
    {
      "measurements": [
        {
          "date": "2025-07-03",
          "kappa": 23.2,
          "lambda": 1.4
        },
        {
          "date": "2025-07-10",
          "kappa": 21.8,
          "lambda": 1.4
        }
      ],
      "settings": { ... }
    }
    """)
    
    # Example: Add a new data point for July 10, 2025
    # add_new_data_point("2025-07-10", 21.8, 1.4)
    
    # Example: Add multiple new data points
    new_data = [
        ("2025-07-10", 21.8, 1.4),
        ("2025-07-17", 20.1, 1.4),
        ("2025-07-24", 18.9, 1.4)
    ]
    
    print("\nTo add new data points, uncomment the following lines:")
    for date, kappa, lambda_val in new_data:
        print(f"# add_new_data_point('{date}', {kappa}, {lambda_val})")
    
    print("\nOr add them all at once:")
    print("# for date, kappa, lambda_val in new_data:")
    print("#     add_new_data_point(date, kappa, lambda_val)")
    
    print("\nAfter adding new data, run: python kappa_report.py")


if __name__ == "__main__":
    main() 