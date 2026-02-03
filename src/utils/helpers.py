def format_student_record(record):
    # Function to format a student record for display
    formatted_record = {
        "enrollment_number": record.get("enrollment_number"),
        "name": record.get("name"),
        "total_marks": record.get("total_marks"),
        "percentage": record.get("percentage"),
        "rank": record.get("rank"),
    }
    return formatted_record

def calculate_percentage(total_marks, max_marks):
    # Function to calculate percentage from total marks
    if max_marks > 0:
        return (total_marks / max_marks) * 100
    return 0

def sort_students_by_rank(students):
    # Function to sort students by their rank
    return sorted(students, key=lambda x: x['rank'])