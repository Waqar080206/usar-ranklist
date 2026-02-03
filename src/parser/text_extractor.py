def extract_student_data(raw_text):
    # Function to process raw text and extract structured student data
    student_records = []
    
    # Split the raw text into lines for processing
    lines = raw_text.splitlines()
    
    for line in lines:
        # Example logic to extract student data
        # This should be replaced with actual extraction logic based on the PDF format
        if line.strip():  # Check if the line is not empty
            parts = line.split()  # Split line into parts
            if len(parts) >= 3:  # Assuming at least 3 parts: name, enrollment number, marks
                student_record = {
                    'name': parts[0],
                    'enrollment_number': parts[1],
                    'marks': list(map(int, parts[2:]))  # Convert marks to integers
                }
                student_records.append(student_record)
    
    return student_records

def clean_extracted_data(student_records):
    # Function to clean and preprocess extracted student data
    cleaned_records = []
    
    for record in student_records:
        # Example cleaning logic
        if 'name' in record and 'enrollment_number' in record:
            cleaned_record = {
                'name': record['name'].strip(),
                'enrollment_number': record['enrollment_number'].strip(),
                'marks': record['marks']
            }
            cleaned_records.append(cleaned_record)
    
    return cleaned_records