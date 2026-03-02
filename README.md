# Process & Gauge Capability Analyzer

Interactive application for process and measurement capability evaluation of machine inspection datasets.

The tool enables structured data filtering, configurable tolerance thresholds, automated fail classification, statistical outlier detection, and automated reporting for quality assessment workflows.

---

## Purpose

This application was developed to replace repetitive manual capability reporting previously performed in Excel.  

It automates the evaluation of machine inspection data, supports root-cause analysis when capability targets are not met, and generates structured, export-ready reports in a consistent format.

---

## Features

- Structured multi-level data filtering (sub-board → component → algorithm → sample → pin)
- Process and measurement capability evaluation
- Configurable global tolerance thresholds
- Automated rule-based fail classification
- Statistical outlier detection
- Dynamic histogram-based failure analysis
- Automated multi-page PDF reporting with formatted summaries and result tables

---

## Tech Stack

- Python
- Pandas
- Streamlit
- Matplotlib
- ReportLab

---

## Project Structure
- app.py              # Application entry point
- data_handler.py     # Data processing and capability calculations
- plotter.py          # Visualization and failure analysis
- report.py           # PDF report generation
- ui/                 # User interface components

---

## Sample Data

A sample dataset is provided in the `sample_data/` folder for testing purposes.

The dataset follows the expected inspection data structure and can be uploaded directly into the application.

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```