import csv

filename = input("What file path do you want to open?")
with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            r = int(row[0]) * int(row[1])
            print(f'{row[0]} * {row[1]} = {row[2]}')
            if r == int(row[2]):
                print("Value 1 and Value 2 match expected result")
            else:
                print("Value 1 and Value 2 do not match expected result")
            line_count += 1
    print(f'Processed {line_count} lines.')
