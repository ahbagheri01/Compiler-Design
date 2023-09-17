import os

rootdir = "./tests/PA3-Resources/TestCases"


def write(address):
    a = ""
    f2 = open("./input.txt", "w")
    with open(address) as f:
        line = f.readline()
        a += (line)
        while line:
            line = f.readline()
            a += (line)
    f2.write(a)
    f2.close()
#f2 = open("./res.txt", "w")
#f2.write("start\n")
#f2.close()

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if "S" in file:
            print(file)
            break
        if file == "expected.txt":
            # os.system(f"echo \"{os.path.join(subdir, file)}\" >> res.txt")
            pass
        elif file == "input.txt":
            write(os.path.join(subdir, file))
            os.system("python3 compiler.py")
            os.system(f"echo \"{os.path.join(subdir, file)}\" >> res.txt")
            os.system("./tester_Linux.out >> res.txt")
            #os.system(f"echo \" expected : {os.path.join(subdir, file)}\" >> res.txt")

        #print(os.path.join(subdir, file))
