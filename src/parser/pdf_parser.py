import pdfplumber
import pandas as pd
import re
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class SubjectResult:
    paper_id: str
    credits: int
    internal: Optional[int] = None
    external: Optional[int] = None
    total: Optional[int] = None
    grade: str = ""

@dataclass
class StudentResult:
    roll_no: str
    name: str
    sid: str = ""
    scheme_id: str = ""
    institution: str = ""
    programme: str = ""
    semester: str = ""
    batch: str = ""
    subjects: List[SubjectResult] = field(default_factory=list)
    total_credits_secured: int = 0
    remarks: str = ""

class BTechResultParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.results: List[StudentResult] = []
        self.current_institution = ""
        self.current_programme = ""
        self.current_semester = ""
        self.current_batch = ""
        self.scheme_info: Dict[str, Dict] = {}  # Paper ID -> Subject info
        
    def parse(self) -> List[StudentResult]:
        """Main parsing method"""
        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                # Check if it's a scheme page or result page
                if "SCHEME OF EXAMINATIONS" in text:
                    self._parse_scheme_page(page)
                elif "RESULT TABULATION SHEET" in text:
                    self._parse_result_page(page, text)
        
        return self.results
    
    def _parse_scheme_page(self, page):
        """Parse scheme page to get subject info"""
        tables = page.extract_tables()
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Check if it's a subject table
            header = table[0]
            if header and 'Paper ID' in str(header):
                for row in table[1:]:
                    if row and len(row) >= 4:
                        paper_id = str(row[0]).strip() if row[0] else ""
                        code = str(row[1]).strip() if row[1] else ""
                        subject = str(row[2]).strip() if row[2] else ""
                        credits = str(row[3]).strip() if row[3] else "0"
                        
                        if paper_id:
                            self.scheme_info[paper_id] = {
                                'code': code,
                                'subject': subject,
                                'credits': int(credits) if credits.isdigit() else 0
                            }
    
    def _parse_result_page(self, page, text: str):
        """Parse result tabulation page"""
        # Extract context info from text
        self._extract_context(text)
        
        tables = page.extract_tables()
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Look for student data table (has Roll no./Name column)
            header = table[0]
            if not header:
                continue
                
            header_str = ' '.join([str(h) for h in header if h])
            
            if 'Roll no' in header_str or 'Institution' in header_str:
                self._parse_student_table(table)
    
    def _extract_context(self, text: str):
        """Extract programme, semester, batch info"""
        # Programme
        prog_match = re.search(r'Programme Name:\s*([^\n]+?)(?:\s*Sem|$)', text)
        if prog_match:
            self.current_programme = prog_match.group(1).strip()
        
        # Semester
        sem_match = re.search(r'Sem\./Year:\s*(\d+)\s*SEMESTER', text)
        if sem_match:
            self.current_semester = sem_match.group(1)
        
        # Batch
        batch_match = re.search(r'Batch:\s*(\d+)', text)
        if batch_match:
            self.current_batch = batch_match.group(1)
        
        # Institution
        inst_match = re.search(r'Institution:\s*([^\n]+?)(?:\s*CS|$)', text)
        if inst_match:
            self.current_institution = inst_match.group(1).strip()
    
    def _parse_student_table(self, table: List[List]):
        """Parse student data from table"""
        i = 1  # Skip header row
        
        while i < len(table):
            row = table[i]
            if not row or len(row) < 3:
                i += 1
                continue
            
            # Check if this row contains student info (Roll no and name)
            student_cell = row[1] if len(row) > 1 else None
            
            if student_cell and isinstance(student_cell, str) and '\n' in student_cell:
                # This is a student row
                student = self._parse_student_row(table, i)
                if student and student.roll_no:
                    self.results.append(student)
            
            i += 1
    
    def _parse_student_row(self, table: List[List], start_idx: int) -> Optional[StudentResult]:
        """Parse a single student's data from table rows"""
        try:
            row = table[start_idx]
            student_cell = str(row[1]) if len(row) > 1 and row[1] else ""
            
            # Parse student info from cell
            lines = student_cell.split('\n')
            roll_no = lines[0].strip() if lines else ""
            name = lines[1].strip() if len(lines) > 1 else ""
            
            sid = ""
            scheme_id = ""
            for line in lines:
                if 'SID:' in line:
                    sid = line.replace('SID:', '').strip()
                elif 'SchemeID:' in line:
                    scheme_id = line.replace('SchemeID:', '').strip()
            
            student = StudentResult(
                roll_no=roll_no,
                name=name,
                sid=sid,
                scheme_id=scheme_id,
                institution=self.current_institution,
                programme=self.current_programme,
                semester=self.current_semester,
                batch=self.current_batch
            )
            
            # Parse paper IDs from first row (format: 015101(3))
            paper_pattern = re.compile(r'(\d{6})\((\d+)\)')
            papers = []
            
            for cell in row[2:]:
                if cell:
                    match = paper_pattern.search(str(cell))
                    if match:
                        papers.append({
                            'paper_id': match.group(1),
                            'credits': int(match.group(2))
                        })
            
            # Get internal/external marks from next rows
            internal_row = table[start_idx + 1] if start_idx + 1 < len(table) else []
            total_row = table[start_idx + 2] if start_idx + 2 < len(table) else []
            
            # Parse marks for each paper
            col_idx = 2  # Start from column 2
            for paper in papers:
                subject = SubjectResult(
                    paper_id=paper['paper_id'],
                    credits=paper['credits']
                )
                
                # Internal marks (odd columns: 2, 4, 6...)
                if col_idx < len(internal_row) and internal_row[col_idx]:
                    try:
                        subject.internal = int(str(internal_row[col_idx]).strip())
                    except:
                        pass
                
                # External marks (even columns: 3, 5, 7...)
                if col_idx + 1 < len(internal_row) and internal_row[col_idx + 1]:
                    try:
                        subject.external = int(str(internal_row[col_idx + 1]).strip())
                    except:
                        pass
                
                # Total and grade from total row
                if col_idx < len(total_row) and total_row[col_idx]:
                    total_str = str(total_row[col_idx]).strip()
                    total_match = re.match(r'(\d+)\(([A-Z+\-]+|F)\)', total_str)
                    if total_match:
                        subject.total = int(total_match.group(1))
                        subject.grade = total_match.group(2)
                    elif total_str in ['A', 'RL', 'C', 'D', 'AP']:
                        subject.grade = total_str
                
                student.subjects.append(subject)
                col_idx += 2  # Move to next paper (2 columns per paper)
            
            # Calculate total credits secured
            student.total_credits_secured = sum(
                s.credits for s in student.subjects 
                if s.grade and s.grade not in ['F', 'A', 'RL', 'C', 'D']
            )
            
            return student
            
        except Exception as e:
            print(f"Error parsing student at row {start_idx}: {e}")
            return None
    
    def calculate_percentage(self, student: StudentResult) -> float:
        """Calculate percentage for a student"""
        total_marks = sum(s.total for s in student.subjects if s.total)
        max_marks = len([s for s in student.subjects if s.total]) * 100
        if max_marks > 0:
            return round((total_marks / max_marks) * 100, 2)
        return 0.0
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame"""
        data = []
        for student in self.results:
            total_marks = sum(s.total for s in student.subjects if s.total)
            max_marks = len([s for s in student.subjects if s.total]) * 100
            percentage = self.calculate_percentage(student)
            
            # Subject-wise marks
            subject_marks = {
                f"{s.paper_id}": f"{s.total}({s.grade})" if s.total else s.grade
                for s in student.subjects
            }
            
            row = {
                'Roll No': student.roll_no,
                'Name': student.name,
                'SID': student.sid,
                'Institution': student.institution,
                'Programme': student.programme,
                'Semester': student.semester,
                'Batch': student.batch,
                'Total Marks': total_marks,
                'Max Marks': max_marks,
                'Percentage': percentage,
                'Credits Secured': student.total_credits_secured,
                **subject_marks
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Sort by percentage descending and add rank
        if not df.empty:
            df = df.sort_values('Percentage', ascending=False)
            df.insert(0, 'Rank', range(1, len(df) + 1))
        
        return df
    
    def to_csv(self, output_path: str):
        """Export results to CSV"""
        df = self.to_dataframe()
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Saved {len(df)} records to {output_path}")
    
    def to_json(self, output_path: str):
        """Export results to JSON"""
        data = []
        for rank, student in enumerate(sorted(self.results, 
                                               key=lambda x: self.calculate_percentage(x), 
                                               reverse=True), 1):
            data.append({
                'rank': rank,
                'roll_no': student.roll_no,
                'name': student.name,
                'sid': student.sid,
                'institution': student.institution,
                'programme': student.programme,
                'semester': student.semester,
                'batch': student.batch,
                'total_marks': sum(s.total for s in student.subjects if s.total),
                'max_marks': len([s for s in student.subjects if s.total]) * 100,
                'percentage': self.calculate_percentage(student),
                'credits_secured': student.total_credits_secured,
                'subjects': [
                    {
                        'paper_id': s.paper_id,
                        'credits': s.credits,
                        'internal': s.internal,
                        'external': s.external,
                        'total': s.total,
                        'grade': s.grade
                    }
                    for s in student.subjects
                ]
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} records to {output_path}")


# Usage
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "..", "FINAL_RESULT_BTECH_USAR_DEC2025.pdf")
    
    print(f"PDF Path: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print("PDF not found!")
        exit(1)
    
    parser = BTechResultParser(pdf_path)
    results = parser.parse()
    
    print(f"\n{'='*60}")
    print(f"Total students parsed: {len(results)}")
    print(f"Subjects in scheme: {len(parser.scheme_info)}")
    print(f"{'='*60}")
    
    # Preview first 5 results
    print("\nTop 5 Students Preview:")
    sorted_results = sorted(results, key=lambda x: parser.calculate_percentage(x), reverse=True)
    
    for i, student in enumerate(sorted_results[:5], 1):
        pct = parser.calculate_percentage(student)
        total = sum(s.total for s in student.subjects if s.total)
        print(f"\n{i}. {student.roll_no} - {student.name}")
        print(f"   Semester: {student.semester}, Total: {total}, Percentage: {pct}%")
        print(f"   Subjects: {[(s.paper_id, s.total, s.grade) for s in student.subjects[:5]]}")
    
    # Export - fix directory issue
    output_dir = os.path.normpath(os.path.join(script_dir, "..", "..", "data", "output"))
    
    # Check if output exists as a file and remove it
    if os.path.isfile(output_dir):
        os.remove(output_dir)
    
    # Create parent directories
    parent_dir = os.path.dirname(output_dir)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    csv_path = os.path.join(output_dir, "parsed_results.csv")
    json_path = os.path.join(output_dir, "parsed_results.json")
    
    parser.to_csv(csv_path)
    parser.to_json(json_path)
    
    print(f"\nFiles saved to: {output_dir}")