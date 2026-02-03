import unittest
from src.parser.pdf_parser import parse_pdf
from src.parser.text_extractor import extract_text
from src.parser.regex_patterns import STUDENT_REGEX, MARKS_REGEX

class TestPDFParser(unittest.TestCase):

    def test_parse_pdf(self):
        # Test parsing a sample PDF file
        pdf_path = 'data/input/sample_results.pdf'
        result = parse_pdf(pdf_path)
        self.assertIsInstance(result, dict)  # Ensure the result is a dictionary
        self.assertIn('students', result)  # Check if 'students' key exists

    def test_extract_text(self):
        # Test extracting text from a sample raw text
        raw_text = "Sample text with student data"
        structured_data = extract_text(raw_text)
        self.assertIsInstance(structured_data, list)  # Ensure the result is a list
        self.assertGreater(len(structured_data), 0)  # Check if data is extracted

    def test_student_regex(self):
        # Test the student regex pattern
        sample_text = "John Doe, Enrollment No: 123456"
        match = STUDENT_REGEX.search(sample_text)
        self.assertIsNotNone(match)  # Ensure the regex matches

    def test_marks_regex(self):
        # Test the marks regex pattern
        sample_text = "Subject: Math, Marks: 85"
        match = MARKS_REGEX.search(sample_text)
        self.assertIsNotNone(match)  # Ensure the regex matches

if __name__ == '__main__':
    unittest.main()