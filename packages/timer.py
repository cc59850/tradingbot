import time

class Timer():
    def __init__(self, interval,func):
        self.interval=interval
        self.func=func

    def run(self):
        t=int(time.time())
        while True:
            if int(time.time())<t+self.interval:
                pass
            else:
                t=int(time.time())
                self.func()


if __name__=='__main__':
    def func():
        print(time.time())
    timer=Timer(1,func)
    timer.run()