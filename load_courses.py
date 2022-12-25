import csv
from uni_data.models import Course
"""
To use this file:
py manage.py shell
>>> exec(open("load_courses.py").read())
"""


print("Copy and paste the entire appropriate subject, courseNumber CSV file")
print("When done, write 5LOSNA and Enter. This will signal the end of input:")
lines = []
while True:
    line = input()
    if line == "5LOSNA":
        break
    lines.append(line)
for i in range(1, len(lines)):
    line = lines[i].split(",")
    Course.objects.create(letter_code=line[0], number=line[1], title=line[2])
