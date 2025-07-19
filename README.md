# Kappa Light Chain Report Generator

This Python program generates a comprehensive PDF report analyzing kappa light chain measurements with pre- and post-venetoclax treatment modeling.

## Features

- **Data Analysis**: Processes kappa and lambda light chain measurements over time
- **Model Fitting**: Uses Gompertz and exponential models to fit treatment phases
- **Projections**: Predicts when VGPR and CR thresholds will be reached
- **PDF Report**: Generates a multi-page PDF with:
  - Linear scale charts with projections
  - Log scale charts for better visualization
  - Detailed data table
  - Mathematical model explanations and IVIG artifact analysis
- **Easy Updates**: Data and notes are stored in JSON files for easy modification

## File Structure

```
KappaReport/
├── kappa_report.py          # Main report generator
├── data.json                # Measurement data and settings
├── notes.json               # Analysis notes and explanations
├── update_data.py           # Helper script for adding new data
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. Make sure you have Python 3.7+ installed
2. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Generate Report

Run the program from the command line (make sure your virtual environment is activated):

```bash
python kappa_report.py
```

### Update Data

To add new measurement data, you can:

1. **Edit `data.json` directly**: Add new measurement entries to the `measurements` array
2. **Use the helper script**: Run `python update_data.py` to see examples of how to add new data points

Example of adding a new data point programmatically:

```python
from update_data import add_new_data_point

# Add a new measurement
add_new_data_point("2025-07-10", 21.8, 1.4)

# Then regenerate the report
# python kappa_report.py
```

### Update Notes

Modify `notes.json` to change the analysis notes and explanations. The notes support string formatting with the following variables:

- `{proj_pre_final}`: Final projection value from pre-venetoclax model
- `{vgpr}`: VGPR threshold value
- `{cr}`: CR threshold value
- `{vgpr_date}`: Projected VGPR date
- `{cr_date}`: Projected CR date

## Data Format

### `data.json`

```json
{
  "measurements": [
    {
      "date": "2025-01-29",
      "kappa": 438.9,
      "lambda": 5.7
    },
    {
      "date": "2025-02-05",
      "kappa": 487.7,
      "lambda": 6.5
    }
  ],
  "settings": {
    "split_date": "2025-04-10",
    "projection_end_date": "2025-10-01",
    "vgpr_threshold": 40.0,
    "cr_threshold": 19.4
  }
}
```

### `notes.json`

```json
{
  "title": "Model Explanation & Detailed IVIG Artifact Analysis",
  "sections": [
    {
      "title": "Section Title",
      "content": ["Line 1 of content", "Line 2 with {formatting}"]
    }
  ]
}
```

## Benefits of New Data Structure

The new structure with individual measurement entries offers several advantages:

- **Easier to read**: Each measurement is a complete entry with date, kappa, and lambda values
- **Easier to edit**: Add new entries without worrying about array alignment
- **Less error-prone**: No risk of misaligned parallel arrays
- **More intuitive**: Each entry represents a single lab result
- **Better for manual editing**: Easy to copy/paste or modify individual measurements

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computing
- matplotlib: Plotting and visualization
- scipy: Scientific computing (for curve fitting)

## Output

The generated PDF report contains:

1. **Page 1**: Linear scale chart showing observed data and model projections
2. **Page 2**: Log scale chart for better visualization of exponential decay
3. **Page 3**: Compressed data table with all measurements
4. **Page 4**: Detailed notes explaining the mathematical models and IVIG artifact analysis

## Notes

- The report analyzes two treatment phases:
  - Pre-Venetoclax (CyBorD): Modeled using Gompertz function
  - Post-Venetoclax (Ven + Dara + Dex): Modeled using exponential decay
- VGPR threshold: <40 mg/L
- CR threshold: <19.4 mg/L
- The analysis includes correction for IVIG artifacts
- The report filename includes the latest data date for easy identification
