import time


class Profile():
    def __init__(self, logPath):
        self.logPath = "%s_%s" % (logPath, str(time.strftime('%Y%m%d%H%M%S')))
        self.start = time.time()
        self.end = time.time()
        self.sectionId = 0

    def set(self):
        self.start = time.time()

    def log(self):
        self.end = time.time()
        duration = (self.end - self.start) * 1000
        with open(self.logPath, "a") as fobj:
            fobj.write("Section %s: %s ms\n" % (self.sectionId, duration))
        self.sectionId += 1

# if __name__=="__main__":
#	profile = Profile("tmp")
#	profile.set()
#	time.sleep(4)
#	profile.log()
#	profile.set()
#	time.sleep(1)
#	profile.log()
