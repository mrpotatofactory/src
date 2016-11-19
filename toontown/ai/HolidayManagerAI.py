from toontown.toonbase import ToontownGlobals

class HolidayManagerAI:
    def __init__(self, air):
        self.air = air
        self.currentHolidays = []
        self.weeklyHolidays = []
        self.configure()
        
    def configure(self):
        holidayList = config.GetString('holiday-list','')
        holidays = holidayList.split(',')
        for holiday in holidays:
            if holiday not in ['',' ']:
                try:
                    holiday = int(holiday)
                except:
                    continue
                self.currentHolidays.append(holiday)
        self.air.newsManager.setHolidayIdList([self.currentHolidays])

        if config.GetBool('want-grand-prix', True):
            self.weeklyHolidays.append([ToontownGlobals.CIRCUIT_RACING, 0]) # Monday
        if config.GetBool('want-fish-bingo', True):
            self.weeklyHolidays.append([ToontownGlobals.FISH_BINGO_NIGHT, 2]) # Wednesday
        if config.GetBool('want-trolley-tracks', True):
            self.weeklyHolidays.append([ToontownGlobals.TROLLEY_HOLIDAY, 3]) # Thursday
        if config.GetBool('want-silly-saturdays', True):
            self.weeklyHolidays.append([ToontownGlobals.SILLY_SATURDAY_BINGO, 5]) # Saturday
        self.air.newsManager.setWeeklyCalendarHolidays([self.weeklyHolidays])

        
    def isHolidayRunning(self, holidayId):
        if holidayId in self.currentHolidays:
            return True

    def appendHoliday(self, holidayId):
        if holidayId not in self.currentHolidays:
            self.currentHolidays.append(holidayId)
            self.air.newsManager.setHolidayIdList([self.currentHolidays])
            return True

    def removeHoliday(self, holidayId):
        if holidayId in self.currentHolidays:
            self. currentHolidays.remove(holidayId)
            self.air.newsManager.setHolidayIdList([self.currentHolidays])
            return True

from otp.ai.MagicWordGlobal import *

@magicWord(chains=[CHAIN_ADM], types=[int])
def startHoliday(holidayId):
    if simbase.air.holidayManager.appendHoliday(holidayId) == True:
        return 'Started Holiday %s' % holidayId
    return 'Holiday %s is already running' % holidayId

@magicWord(chains=[CHAIN_ADM], types=[int])
def endHoliday(holidayId):
    if simbase.air.holidayManager.removeHoliday(holidayId) == True:
        return 'Ended Holiday %s' % holidayId
    return 'Holiday %s already ended' % holidayId
    