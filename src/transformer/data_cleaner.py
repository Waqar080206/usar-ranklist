def clean_data(raw_data):
    cleaned_data = []
    for record in raw_data:
        # Remove any leading or trailing whitespace
        record = {key: value.strip() for key, value in record.items() if value}
        
        # Ensure all necessary fields are present
        if 'enrollment_number' in record and 'marks' in record:
            cleaned_data.append(record)
    
    return cleaned_data

def preprocess_data(cleaned_data):
    for record in cleaned_data:
        # Convert marks to integers
        record['marks'] = [int(mark) for mark in record['marks']]
        
        # Calculate total and percentage
        record['total'] = sum(record['marks'])
        record['percentage'] = record['total'] / len(record['marks'])
    
    return cleaned_data