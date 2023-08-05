import subprocess
import re
from IPython.display import display, Markdown
from tabulate import tabulate
from excmanager.Util import Util

def radb_raw(db_path, expression):
    return subprocess.run(["radb", db_path], input = expression, encoding = 'utf8', capture_output = True)

def extract_tuples_and_attributes(db_path, expression):
    result = radb_raw(db_path, expression)

    #print(result.stdout)

    if "ra> " in result.stdout:
        output = result.stdout.split("ra> ")[1]
    else:
        output = result.stdout

    if ("ERROR: " in output):
        print("Error: " + output.split("ERROR: ")[1])
        return False

    # Warnings are treated as errors - don't give output, don't return anything that could be handed in as a solution
    if ("WARNING: " in output):
        print("Error: " + output.split("WARNING: ")[1].split("\n")[0])
        return False

    lines = output.split("\n")
    attributes = re.findall("[(| ]\w+:", lines[0])
    attributes = list(map(lambda s: s[1:-1], attributes))
    tuples = []
    for line in lines[2:]:
        if line.startswith("-"):
            break
        tuples.append(list(map(str.strip, line.split(","))))
    return tuples, attributes

def radb_evaluate(db_path, expression):
    try:
        x = extract_tuples_and_attributes(db_path, expression)
        if (x == False):
            return False
        else:
            tuples, attributes = x
            table = tabulate(tuples, attributes, tablefmt="github")
            display(Markdown(table))
            return expression
    except:
        print("No or wrong expression given.")
        return False


def radb_check(db_path, expression, attributes_solution, tuples_solution, levenshtein_threshold=1):
    x = extract_tuples_and_attributes(db_path, expression)
    if (x == False):
        return False
    else:
        tuples, attributes = x
        return Util.check_table(attributes_solution, tuples_solution, attributes, tuples, levenshtein_threshold, False)
