from toontown.toonbase.ToontownGlobals import *
import RegenTreasurePlannerAI
import DistributedFFTreasureAI

class FFTreasurePlannerAI(RegenTreasurePlannerAI.RegenTreasurePlannerAI):
    def __init__(self, zoneId):
        self.healAmount = 8
        RegenTreasurePlannerAI.RegenTreasurePlannerAI.__init__(self, zoneId, DistributedFFTreasureAI.DistributedFFTreasureAI, 'FFTreasurePlanner', 20, 5)

    def initSpawnPoints(self):
        self.spawnPoints = [
            (50.620, -48.766, 0.025),
            (-7.282, 8.387, 2.025),
            (-58.286, -7.871, 0.025),
            (-45.659, -81.27, 0.025),
            (-110.788, 41.453, 0.025),
            (-36.547, 151.893, 0.025),
            (-103.000, 67.000, 0.025),
            (-12.310, 95.114, 0.025),
            (69.655, 127.853, 0.025),
            (109.524, -8.199, 0.025),
            (57.549, 46.988, 0.025),
            (104.648, 80.214, 0.025)]
        return self.spawnPoints
