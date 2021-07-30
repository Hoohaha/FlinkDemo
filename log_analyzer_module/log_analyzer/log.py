
import os


def load( filepath):
    context = open(filepath).read().split("\n")
    return context

err_path = "C:/clogs/error/"
files = os.listdir(err_path)


buffer = list()
for fname in files:
    all_lines = load(err_path+fname)
    for line in all_lines:
        if line not in buffer:
            buffer.append(line)


content = "\n".join(buffer)
file = open("false.txt", "w")
file.write(content)
file.close()