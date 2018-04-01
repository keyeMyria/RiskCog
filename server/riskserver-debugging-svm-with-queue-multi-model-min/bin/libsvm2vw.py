"convert libsvm file to vw format"
"skip malformed lines"


def libsvm2vw(input_file, output_file):
    print '## TRACE ##', 'converts libsvm to vw', input_file, output_file
    i = open(input_file)
    o = open(output_file, 'wb')

    for line in i:
        try:
            if "nan" in line.lower():
                continue
            y, x = line.split(" ", 1)

            if float(y) != 1.0:
                y = '-1'

        # ValueError: need more than 1 value to unpack
        except ValueError:
            print "line with ValueError (skipping):"
            print line
            continue

        nums = [float(i) for i in x.replace("|", " ").replace("n", " ").replace(":", " ").split()]

        cont = False
        for k in nums:
            if k > 1000.00 or k < -1000.0:
                cont = True

        if cont:
            continue

        new_line = y + " |n " + x
        o.write(new_line)
