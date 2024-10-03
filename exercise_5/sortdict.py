list_of_dicts = [
    {'student_id': 8675309, 'grade': 80},
    {'student_id': 8770909, 'grade': 70},
    {'student_id': 8553210, 'grade': 60},
]

by_grade = sorted(list_of_dicts, key=lambda element: element['student_id'])

print(by_grade)