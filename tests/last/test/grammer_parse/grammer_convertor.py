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
    line = line.replace("EPSILON","null")
    g = line.split("->")
    left = g[0].replace(" ", "").strip()
    right = g[1].split("|")
    right_g = []
    for word in right:
        word = word.strip()
        w = word.split()
        grammer_for_jason_format.append({"left": left, "right": w})
        right_g.append(w)
    grammer[left] = right_g

with open('G.txt') as f:
    line = f.readline()
    analysis(line)
    while line:
        line = f.readline()
        analysis(line)
json.dump( grammer, open( "grammer.json", 'w' ) )

# Read data from file:
data = json.load( open( "grammer.json" ) )
json.dump( grammer_for_jason_format, open( "jsongrammer.json", 'w' ) )

# Read data from file:
data = json.load( open( "jsongrammer.json" ) )
print(data)