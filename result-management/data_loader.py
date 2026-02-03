"""
Data loader - creates embedded_data.py for Vercel deployment
"""

import json
from pathlib import Path

def main():
    # Find data file
    current_dir = Path(__file__).resolve().parent
    paths = [
        current_dir / "data" / "parsed_results.json",
        
        current_dir.parent / "data" / "output" / "parsed_results.json",
    ]
    
    data_file = None
    for p in paths:
        if p.exists():
            data_file = p
            break
    
    if not data_file:
        print("❌ Data file not found!")
        return
    
    print(f"📂 Reading: {data_file}")
    
    # Load JSON
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} records")
    
    # Write Python file line by line
    output = current_dir / "embedded_data.py"
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write('# Auto-generated - DO NOT EDIT\n')
        f.write('STUDENT_DATA = [\n')
        
        for i, student in enumerate(data):
            # Convert each student dict to Python syntax
            student_str = '    {\n'
            
            for key, value in student.items():
                if key == 'subjects':
                    # Handle subjects array
                    student_str += f'        "subjects": [\n'
                    for subj in value:
                        subj_parts = []
                        for sk, sv in subj.items():
                            if sv is None:
                                subj_parts.append(f'"{sk}": None')
                            elif isinstance(sv, str):
                                subj_parts.append(f'"{sk}": "{sv}"')
                            else:
                                subj_parts.append(f'"{sk}": {sv}')
                        student_str += '            {' + ', '.join(subj_parts) + '},\n'
                    student_str += '        ],\n'
                elif value is None:
                    student_str += f'        "{key}": None,\n'
                elif isinstance(value, str):
                    # Escape quotes in strings
                    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                    student_str += f'        "{key}": "{escaped}",\n'
                elif isinstance(value, bool):
                    student_str += f'        "{key}": {value},\n'
                else:
                    student_str += f'        "{key}": {value},\n'
            
            student_str += '    },\n'
            f.write(student_str)
            
            if (i + 1) % 500 == 0:
                print(f"  Written {i + 1}/{len(data)}...")
        
        f.write(']\n')
    
    print(f"✅ Created: {output}")
    print(f"✅ Size: {output.stat().st_size / 1024:.1f} KB")
    
    # Verify no 'null' in file
    with open(output, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'null' in content:
        print("❌ ERROR: File still contains 'null'!")
    else:
        print("✅ No 'null' found - file is clean!")
    
    # Test import
    try:
        exec(compile(content, str(output), 'exec'))
        print("✅ Python syntax valid!")
    except Exception as e:
        print(f"❌ Syntax error: {e}")

if __name__ == "__main__":
    main()