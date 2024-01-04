'''
TODO Complete this file by following the instructions in the lab exercise.
'''

strings = ['This', 'list', 'is', 'now', 'all', 'together']

i = 0
for i in range (0, len(strings)):
    print(strings[i], end = "")
    i = i + 1
    if i < len(strings):
        print(" ", end = "")
print("")
