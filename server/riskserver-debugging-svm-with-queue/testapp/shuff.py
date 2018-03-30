import random


def shuff(path):
    f = open(path, "r")
    info = f.readlines()
    f.close

    random.shuffle(info)

    f = open(path, "w")
    for line in info:
        f.write(line)
    f.close
