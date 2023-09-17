import numpy as np

n = 15
nums = [np.random.choice([0, 1], size=n, p=[.95, .05]) for _ in range(n)]
x = 0
for i in range(n):
    for j in range(n):
        if (nums[i][j] == 1):
            x += 1
st = str(n) + " " + str(x) + "\n"
for i in range(n):
    for j in range(n):
        if (nums[i][j] != 0):
            st += str(i + 1) + " " + str(j + 1) + "\n"

# print(nums)
table = ""
print(st)
for i in range(n):
    for j in range(n):
        if nums[i][j] == 1:
            table+="*"
        else:
            table+="-"
    table+="\n"
#print(table)