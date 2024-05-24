
class TrainQueue:
    def __init__(self):
        self.trains = []
        
    def Append(self, osnm, rtnm, signm, blknm):
        self.trains.append([osnm, rtnm, signm, blknm])

    def Get(self):
        if len(self.trains) == 0:
            return None

        rv = self.trains[0]
        self.trains = self.trains[1:]
        return rv
