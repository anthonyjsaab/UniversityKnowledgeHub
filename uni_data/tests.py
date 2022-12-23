import csv

filenames = ['courses-Spring21-22.csv', 'courses-Fall22-23.csv', 'courses-Summer21-22.csv']
dump = []
for fn in filenames:
    nh = open(fn)
    reader = csv.DictReader(nh)
    for r in reader:
        dump.append((r['subject'], r['courseNumber']))
    nh.close()
s = set(dump)
clean = list(dump)
clean.sort()
with open('unique_courses_sorted.csv') as f:
    c = csv.DictWriter(f, ['subject', 'courseNumber'])
    c.writeheader()
    c.writerows(clean)
