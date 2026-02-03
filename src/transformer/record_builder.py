def build_student_record(cleaned_data):
    student_records = []

    for entry in cleaned_data:
        record = {
            "enrollment_number": entry.get("enrollment_number"),
            "name": entry.get("name"),
            "subjects": entry.get("subjects"),
            "total_marks": sum(entry.get("subjects").values()),
            "percentage": (sum(entry.get("subjects").values()) / entry.get("total_possible_marks")) * 100,
        }
        student_records.append(record)

    return student_records

def transform_to_json(student_records):
    import json
    return json.dumps(student_records, indent=4)