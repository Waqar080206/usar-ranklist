# USAR Ranklist — Automated Result Parsing and Ranking System

## Overview
USAR Ranklist is a lightweight data engineering project designed to transform unstructured IPU result PDFs into a structured, searchable, and ranked student result interface. The system automates the extraction of student and subject data, computes totals and percentages, ranks students semester-wise, and presents the information through a user-friendly web interface.

## Problem Statement
IPU publishes results in static PDF formats that:
- Are not searchable in a meaningful way
- Do not provide rank lists
- Do not allow easy comparison between students
- Contain semi-structured tabular data that is difficult to analyze

This project addresses these issues by converting PDFs into structured data and providing meaningful insights.

## Core Workflow
1. Result PDF
2. Text Parsing
3. Structured JSON
4. Ranking Logic
5. Web Interface

## Key Features
- Automated parsing of IPU result PDFs using Python
- Conversion of semi-structured text into structured student records
- Subject-wise and semester-wise data modeling
- Automatic calculation of total marks, percentage, and semester rank
- Searchable interface by enrollment number
- Easily reusable for future result PDFs by simply replacing the input file

## Tech Stack
- **Python**: Used for PDF parsing (pdfplumber, regex)
- **JavaScript**: Used for ranking and calculations
- **JSON**: Used as a data store
- **HTML**: Used for the user interface

## Technical Concepts Demonstrated
- Parsing semi-structured documents
- Data modeling and transformation
- Ranking algorithms
- Lightweight data pipeline design
- Separation of data processing and presentation layer

## Setup Instructions
1. Clone the repository.
2. Navigate to the project directory.
3. Install the required Python packages using:
   ```
   pip install -r requirements.txt
   ```
4. Install the necessary JavaScript dependencies using:
   ```
   npm install
   ```
5. Place the input PDF files in the `data/input` directory.
6. Run the parsing and transformation scripts to generate structured data.
7. Open `web/index.html` in a browser to view the results.

## Usage Guidelines
- Ensure that the input PDF files are in the correct format as expected by the parser.
- The output JSON files will be saved in the `data/output` directory.
- Use the web interface to search for student results by enrollment number and view the ranked list.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.