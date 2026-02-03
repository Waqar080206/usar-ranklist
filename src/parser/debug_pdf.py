import pdfplumber
import os

# Path to PDF
pdf_path = os.path.join(os.path.dirname(__file__), "..", "FINAL_RESULT_BTECH_USAR_DEC2025.pdf")

print(f"Opening: {pdf_path}")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    # Extract text from first 3 pages to understand structure
    for i in range(min(3, len(pdf.pages))):
        print(f"\n{'='*80}")
        print(f"PAGE {i+1}")
        print("="*80)
        
        page = pdf.pages[i]
        text = page.extract_text()
        
        if text:
            # Print full text of first page, partial for others
            if i == 0:
                print(text)
            else:
                print(text[:3000])
        
        # Check for tables
        tables = page.extract_tables()
        if tables:
            print(f"\n--- Found {len(tables)} table(s) ---")
            for j, table in enumerate(tables):
                print(f"\nTable {j+1} ({len(table)} rows):")
                for row in table[:10]:  # First 10 rows
                    print(row)