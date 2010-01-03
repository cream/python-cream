import math
import time
import gtk
import gobject
import cream.util.events

FPS = 30

CURVE_LINEAR = 0
CURVE_SINE = 1

class Curve:

    def __init__(self, time, type, fps=FPS):

        self.lock = cream.util.events.Event()

        self.frame = 0

        self.frames = []

        frames_num = int((float(time) / 1000.0) * fps)

        self.time = 1000/fps

        if type == CURVE_LINEAR:
            for i in xrange(1, frames_num+1):
                self.frames.append((1.0/frames_num)*i)
        elif type == CURVE_SINE:
            for i in xrange(1, frames_num+1):
                self.frames.append(math.sin(math.radians((1.0/frames_num)*i*90)))


    def run(self, callback, *args):

        self.callback = callback

        self.frame = 0

        c = 0

        for i in self.frames:
            last = False
            if i == self.frames[-1]:
                last = True
            gobject.timeout_add(c * self.time, self.update, i, last, args)
            c += 1

        self.lock.clear()

        #self.update()


    def update(self, state, last=False, args=[]):

        #result = self.callback(self.frames[self.frame])
        result = self.callback(state, *args)

        #t = self.time - int((time.time() - start) * 1000)

        #if t < 0:
        #    t = 0

        #if self.frames[self.frame] != self.frames[-1] and result != False:
        #    self.frame += 1
        #    gobject.timeout_add(self.time, self.update)
        if last:
            self.lock.set()

        return False


    def wait(self):

        self.lock.wait()
