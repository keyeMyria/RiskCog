def median(lst):
    if not lst:
        return
    if len(lst) % 2 == 1:
        return lst[len(lst) // 2]
    else:
        sum = lst[len(lst) // 2 - 1]
        sum = sum + lst[len(lst) // 2]
        sum = sum / 2.0
        return sum


def check_is_lie(file_name):
    print '## TRACE ##', 'check if the file is a lie: ', file_name
    f = open(file_name)
    lines = f.readlines();
    f.close()

    gx = []
    gy = []
    gz = []
    for i in range(0, len(lines), 9):
        gx.append(lines[i + 6])
        gy.append(lines[i + 7])
        gz.append(lines[i + 8])

    gx = [float(x) for x in gx]
    gy = [float(x) for x in gy]
    gz = [float(x) for x in gz]

    if (abs(median(gx)) <= 1.5 and
                abs(median(gy)) <= 1.5 and
                abs(median(gz)) < 10 and
            abs(median(gz) >= 9)):
        return True

    return False
