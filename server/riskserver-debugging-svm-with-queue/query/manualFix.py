#!/usr/bin/python

import math
import sys

TRUE_LABEL = 1
FALSE_LABEL = -1


# parse the data in VW format fromt the given file to a list, where each element's last number is the prediction results
def parser(VWFilePath):
    resLst = []
    try:
        with open(VWFilePath, 'r') as fobj:
            for l in fobj.readlines():
                l = l.strip()
                tokens = l.split(' ')
                decision = int(tokens[0])
                featureValLst = []
                for elem in tokens:
                    if elem.find(":") > 0:
                        featureValLst.append(float(elem.split(':')[1]))
                featureValLst.append(decision)
                resLst.append(featureValLst)
        return resLst
    except Exception as e:
        print "Error is parse %s, %s" % (VWFilePath, str(e))
        sys.exit(-1)


def dist(v1, v2):
    if len(v1) != len(v2):
        print "Error in get dist between two vectors, dimensions not equal"
        sys.exit(-1)
    else:
        res = 0
        for index in range(len(v1)):
            res = res + (v1[index] - v2[index]) ** 2
        return math.sqrt(res)


# return a conrrected lst based on the source lst and user input correctLst
def correct(sourceLst, correctLst):
    resLst = []
    # fix the original set
    for sourceElem in sourceLst:
        sourceFeature = sourceElem[:len(sourceElem) - 1]
        sourceDecision = sourceElem[-1]
        isCorrected = False
        for correctElem in correctLst:
            correctFeature = correctElem[:len(correctElem) - 1]
            distance = dist(sourceFeature, correctFeature)
            if distance < DIST_THRESHOLD:
                if isTrue and sourceDecision == FALSE_LABEL:
                    print "Remove %s" % sourceElem
                    isCorrected = True
                    break
                elif not isTrue and sourceDecision == TRUE_LABEL:
                    print "Remove %s" % sourceElem
                    isCorrected = True
                    break

        if not isCorrected:
            resLst.append(sourceElem)

            # append the correct set
    for correctElem in correctLst:
        if isTrue:
            correctElem[-1] = TRUE_LABEL
        else:
            correctElem[-1] = FALSE_LABEL
        resLst.append(correctElem)
        print "Add %s" % correctElem
    return resLst


def dump(resLst, outputfiile):
    with open(outputfiile, 'w') as fobj:
        for elem in resLst:
            line = "%s |n" % elem[-1]
            for index in range(len(elem) - 1):
                line = line + " %s:%s" % (index, elem[index])
            fobj.write(line + "\n")
        fobj.close()
        print("Correct traingin set dumped to %s" % outputfiile)


if __name__ == "__main__":
    try:
        VWSourceFilePath = sys.argv[1]

        CorrectSampleFilePath = sys.argv[2]

        isTrue = False
        if sys.argv[3] == '1' or sys.argv[3].lower() == 'true':
            isTrue = True

        DIST_THRESHOLD = float(sys.argv[4])

        outPutFilePath = sys.argv[5]
    except:
        print "invalid command invocation"
        print "python manualFix.py originalTraingSetFilePath UserCorrectedFilePath true/false threshold[float, recommended 2.0] outputfilePath"
        sys.exit(-1)

    sourceLst = parser(VWSourceFilePath)
    correctLst = parser(CorrectSampleFilePath)
    correctedLst = correct(sourceLst, correctLst)
    dump(correctedLst, outPutFilePath)
