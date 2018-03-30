import random


class ProbController():
    def __init__(self, prob):
        if prob < 0 or prob > 1.0:
            print "Invalid probability, set as default 0.5"
            prob = 0.5
        self.thres = int(100 * prob)
        if self.thres == 0:
            self.thres = 1

    def isHit(self):
        randNum = random.randint(0, 100)
        print self.thres, randNum
        return randNum <= self.thres

# if __name__=="__main__":
#	pc = ProbController(0.77)
#	print pc.isHit()
