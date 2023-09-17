import json

# Serialize data into file:

grammer_for_jason_format = []
grammer = {};


def make_grammer(g):
    g = g.split(" ")


def analysis(line):
    if (len(line) == 0):
        return
    line = line.strip()
    line = line.replace("EPSILON", "null")
    line = line.replace("\u03b5", "null")
    g = line.split("->")
    left = g[0].replace(" ", "").strip()
    right = g[1].split("|")
    right_g = grammer.get(left, [])
    for word in right:
        word = word.strip()
        w = word.split()
        grammer_for_jason_format.append({"left": left, "right": w})
        right_g.append(w)
    grammer[left] = right_g


with open('grammer.txt') as f:
    line = f.readline()
    analysis(line)
    while line:
        line = f.readline()
        analysis(line)
json.dump(grammer, open("grammer.json", 'w'))
json.dump(grammer, open("../parser_utils/grammer.json", 'w'))

# Read data from file:
data = json.load(open("grammer.json"))
json.dump(grammer_for_jason_format, open("jsongrammer.json", 'w'))

# Read data from file:
data = json.load(open("grammer.json"))
print(len(data))

f2 = open("../parser_utils/grammer.txt", 'w')
a = ""
with open('grammer.txt') as f:
    line = f.readline()
    a += (line)
    while line:
        line = f.readline()
        a += (line)
f2.write(a)
f2.close()
