import subprocess
import argparse

parser = argparse.ArgumentParser(description="Grader for Exercise 1")
parser.add_argument('filename')

args = parser.parse_args()
print(f"Grading {args.filename}")

total_points = 0

def test(description, input_str, output_str):
    print(f"  Testing {description}...")
    try:
        output = subprocess.check_output(['py', args.filename], input=input_str, text=True)
    except subprocess.CalledProcessError as e:
        print("  FAILED script returned an eror")
    else:
        if output == output_str:
            print("  PASSED")
            return True
        else:
            print(f"  FAILED invalid output: {output}")
    return False

if test("first guess correct", "Hello world\n", "Good job\n"):
    total_points += 1
if test("second guess correct", "invalid\nHello world\n", "Please try again\nGood job\n"):
    total_points += 1
if test("third guess correct", "invalid\ninvalid\nHello world\n", "Please try again\nPlease try again\nGood job\n"):
    total_points += 1
if test("attempts exceeded", "invalid\ninvalid\ninvalid\n", "Please try again\nPlease try again\nPlease try again\nAttempts exceeded\n"):
    total_points += 1

print(f"  Final grade: {total_points}/4")
