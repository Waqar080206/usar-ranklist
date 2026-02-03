import re

# Regular expression patterns for extracting data from the result PDFs

# Pattern to match student names
STUDENT_NAME_PATTERN = r'(?<=Name:\s)([A-Za-z\s]+)'

# Pattern to match enrollment numbers
ENROLLMENT_NUMBER_PATTERN = r'(?<=Enrollment No:\s)(\d{10})'

# Pattern to match subject marks
SUBJECT_MARKS_PATTERN = r'(\w+)\s+(\d{1,3})'

# Pattern to match total marks
TOTAL_MARKS_PATTERN = r'Total Marks:\s*(\d{1,3})'

# Pattern to match percentage
PERCENTAGE_PATTERN = r'Percentage:\s*(\d{1,3}\.\d{1,2})%'