from direct.directnotify import DirectNotifyGlobal
from toontown.parties.DecorBase import DecorBase
from toontown.parties.ActivityBase import ActivityBase

class PartyInfoBase:
    notify = DirectNotifyGlobal.directNotify.newCategory('PartyInfoBase')

    def __init__(self, hostId, isPrivate, activityList, decors):
        self.partyId = hostId
        self.hostId = hostId
        self.isPrivate = isPrivate
        
        self.activityList = []
        for oneItem in activityList:
            newActivity = ActivityBase(oneItem[0], oneItem[1], oneItem[2], oneItem[3])
            self.activityList.append(newActivity)

        self.decors = []
        for oneItem in decors:
            newDecor = DecorBase(oneItem[0], oneItem[1], oneItem[2], oneItem[3])
            self.decors.append(newDecor)

    def getActivityIds(self):
        activities = []
        for activityBase in self.activityList:
            activities.append(activityBase.activityId)

        return activities

    def __str__(self):
        string = 'partyId=%d ' % self.partyId
        string += 'hostId=%d ' % self.hostId
        string += 'isPrivate=%s ' % self.isPrivate
        string += 'activityList=%s ' % self.activityList
        string += 'decors=%s ' % self.decors
        string += '\n'
        return string

    def __repr__(self):
        return str(self)

class PartyInfo(PartyInfoBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('PartyInfo')

class PartyInfoAI(PartyInfoBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('PartyInfo')
