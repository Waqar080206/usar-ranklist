import unittest
from src.transformer.data_cleaner import clean_data
from src.transformer.record_builder import build_student_records

class TestTransformer(unittest.TestCase):

    def setUp(self):
        self.raw_data = [
            {"name": "John Doe", "enrollment_number": "12345", "marks": [85, 90, 78]},
            {"name": "Jane Smith", "enrollment_number": "12346", "marks": [88, 92, 80]},
        ]
        self.cleaned_data = clean_data(self.raw_data)

    def test_clean_data(self):
        self.assertIsInstance(self.cleaned_data, list)
        self.assertGreater(len(self.cleaned_data), 0)

    def test_build_student_records(self):
        student_records = build_student_records(self.cleaned_data)
        self.assertIsInstance(student_records, list)
        self.assertEqual(len(student_records), len(self.cleaned_data))
        self.assertIn("total_marks", student_records[0])
        self.assertIn("percentage", student_records[0])
        self.assertIn("rank", student_records[0])

if __name__ == '__main__':
    unittest.main()