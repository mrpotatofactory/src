from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import FSM
from direct.distributed.DistributedObjectUD import *
from toontown.toon.ToonDNA import ToonDNA, getSpeciesName
import TopToonsGlobals
import time, cPickle, random
import datetime, json
import urllib
import urllib2
import hashlib

def getCurrentMonth():
    dt = datetime.date.today()
    month = dt.month
    year = dt.year
    return year * 100 + month
    
def getPrevMonth():
    current = getCurrentMonth()
    year, month = divmod(current, 100)
    month -= 1
    if not month:
        month = 12
        year -= 1
        
    return year * 100 + month
   
def getNextMonth():
    current = getCurrentMonth()
    year, month = divmod(current, 100)
    month += 1
    if month > 12:
        month = 1
        year += 1
        
    return year * 100 + month
    
def timeToNextMonth():
    now = datetime.datetime.now()
    year, month = divmod(getNextMonth(), 100)
    return (datetime.datetime(year, month, 1) - now).total_seconds()
    
def getEmptySiteToonsColl(month):
    coll = {} 
    
    start = TopToonsGlobals._CAT_BEGIN
    end = TopToonsGlobals._CAT_END
    while start <= end:
        coll[str(start)] = {}
        start *= 2
    
    coll['month'] = month
    return coll

class SiteUploadFSM(FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('SiteUploadFSM')
    URL = config.GetString('toptoons-api-endpoint', 'http://toontownnext.net/toptoons/post/')
    
    def __init__(self, mgr, data):
        FSM.__init__(self, 'SiteUploadFSM')
        
        self.mgr = mgr
        self.data = {}
        self.month = data.pop('month')
        for category, avs in data.items():
            self.data[int(category)] = sorted(avs.items(), key=lambda x: -x[1])

        self.__cat = TopToonsGlobals._CAT_BEGIN
        self.__responses = {}
        self.__cache = {}
        self.__waiting = {}
        self.__dataToSend = {}
        self.__failures = -1
        
        self.demand('QueryAvatars')
        
    def enterQueryAvatars(self):
        avs = self.data[self.__cat]
        cutoff = self.__failures
        if cutoff == -1:
            cutoff = 5
        selected, remaining = avs[:cutoff], avs[cutoff:]
        self.data[self.__cat] = remaining
            
        self.__waiting = {int(x[0]): x[1] for x in selected}
        avIds = self.__waiting.keys()
        for avId in avIds:
            if avId in self.__cache:
                self.__responses[avId] = (self.__cache[avId][0], self.__waiting.pop(avId))
                
        self.__failures = 0
        for avId in self.__waiting:
            def response(x, y, avId=avId):
                self.__handleToon(avId, x, y)
                
            self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, avId, response)
            
        if not self.__waiting:
            self.demand('SortResults')
            
    def __handleToon(self, avId, dclass, fields):
        if avId not in self.__waiting:
            return
        
        if dclass != self.mgr.air.dclassesByName['DistributedToonUD']:
            self.__failures += 1
            self.notify.warning('%d query failed!' % avId)
            del self.__waiting[avId]
            if not self.__waiting:
                self.demand('QueryAvatars')
            return
        
        name = fields['setName'][0]
        hp = fields['setMaxHp'][0]
        
        dna = ToonDNA(fields['setDNAString'][0])
        species = getSpeciesName(dna.head)
        color = dna.headColor
        
        if species == 'pig':
            dna = 'pig'
            
        else:
            if species == 'cat' and color == 26:
                dna = 'blackcat'
            
            else:
                if color > 23:
                    color = 0
                
                dna = '%s_%s_%d' % (species, dna.head[1:], color)
        
        self.__responses[avId] = ((name, dna, hp), self.__waiting.pop(avId))

        if not self.__waiting:
            self.demand('QueryAvatars')
            
    def enterSortResults(self):
        responses = sorted(self.__responses.values(), key=lambda x: -x[-1])
        self.__dataToSend[self.__cat] = responses
        self.__cache.update(self.__responses)
        self.__failures = -1
        self.__responses = {}
        self.__cat *= 2
        if self.__cat * 2 == TopToonsGlobals._CAT_END:
            self.demand('Upload')
            return
            
        self.demand('QueryAvatars')
        
    def enterUpload(self):
        self.__dataToSend['month'] = self.month
        
        (success, error), res = self.post(self.URL, self.__dataToSend)
        print (success, error), res
        
        if success:
            self.mgr.d_notifyWinner(TopToonsGlobals.DOID_SITE_INFO, '')
        
    def post(self, url, data):
        headers = {'User-Agent' : 'TTUberAgent'}
        
        innerData = json.dumps(data)
        hmac = hashlib.sha512(innerData + self.mgr.air.getApiKey()).hexdigest()
        
        data = 'data=%s' % urllib.quote(innerData)
        data += '&hmac=%s' % urllib.quote(hmac)
        
        success = True
        error = None
        res = {}
        
        try:
            req = urllib2.Request(url, data, headers)
            res = json.loads(urllib2.urlopen(req).read())
            success = res['success']
            error = res.get('error')
            
        except Exception as e:
            if hasattr(e, 'read'):
                with open('../e.html', 'wb') as f:
                    f.write(e.read())
                
            success = False
            error = str(e)
                
        return (success, error), res
        
class DistributedTopToonsManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTopToonsManagerUD')
    
    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)
        
        # Challenges
        if self.air.dbConnType == 'mongodb':
            coll = self.air.dbGlobalCursor.topToons.find_one({'x': 0})
            data = {}
            if coll:
                data = {'currentSeed': coll['currentSeed'], 'ranking': coll['ranking'],
                        'history': coll['history'], 'startTime': coll['startTime']}

        else:
            self.notify.warning('Not using mongodb, challenge data will be non-persistent')
            data = {}
            
        self.currentSeed = data.get('currentSeed', int(time.time()))
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        
        defaultRanking = []
        defaultHistory = []
        
        if config.GetBool('top-toons-fake-toons', False):
            for i in xrange(20):
                avId = 0
                name = 'Fake Toon %d' % (i + 1)
                score = int(self.currentChallenge.getAmount() * random.random())
                defaultRanking.append([avId, name, score])
                
            defaultRanking.sort(key=lambda x: x[2])
            
            for i in xrange(20):
                name = 'Fake History Toon %d' % (i + 1)
                tim = random.randint(600, 180000)
                seed = int(i + time.time())
                defaultHistory.append([name, tim, seed])
        
        self.history = data.get('history', defaultHistory)
        self.ranking = data.get('ranking', defaultRanking)
        self.ranking.sort(key=lambda x: x[2])
        self.__startTime = data.get('startTime', time.time())
        self.save()
        
        self.accept('topToonsManager-AI-request', self.requestData)
        self.accept('topToonsManager-AI-score', self.score)
        
        # Top toons (codename site toons)
        self.__curMonth = getCurrentMonth()
        coll = None
        if self.air.dbConnType == 'mongodb':
            coll = self.air.dbGlobalCursor.siteToons.find_one({'month': self.__curMonth})
            if not coll:
                lastMonthColl = self.air.dbGlobalCursor.siteToons.find_one({'month': getPrevMonth()})
                if lastMonthColl:
                    self.__uploadLastMonth(lastMonthColl)
                    
        if not coll:
            coll = getEmptySiteToonsColl(self.__curMonth)
            
        self.__topToonsData = coll
        self.__topToonsData.pop('_id', None)
        
        self.accept('topToonsManager-AI-score-site', self.__topToonsScore)
        self.waitForNextMonth()
        
    def newChallenge(self, winnerName):
        self.history.append([winnerName, int(time.time() - self.__startTime), self.currentSeed])
        
        self.currentSeed = int(time.time())
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        self.ranking = []
        self.__startTime = time.time()
        
    def save(self):
        if self.air.dbConnType == 'mongodb':
            data = {}
            data['currentSeed'] = self.currentSeed
            data['history'] = self.history
            data['ranking'] = self.ranking
            data['startTime'] = self.__startTime
        
            self.air.dbGlobalCursor.topToons.update({'x': 0}, {'$set': data}, upsert=True)

    def requestData(self):
        self.d_updateData(self.air.getMsgSender())
        
    def d_updateData(self, channel=None):
        if channel is None:
            channel = 10
            
        self.sendUpdateToChannel(channel, 'setData', [self.currentSeed, self.ranking, self.history, self.__startTime])
        self.air.sendNetEvent('topToonsManager-UD-newChallenge', [self.currentSeed, self.ranking, self.history, self.__startTime])
        
    def score(self, challengeSeed, avId, score, name):
        if challengeSeed != self.currentSeed:
            self.d_updateData(self.air.getMsgSender())
            return
            
        if avId == 0:
            return
            
        for i, (_avId, _, _score) in enumerate(self.ranking):
            if _avId == avId:
                _score += score
                break
                
        else:
            self.ranking.append(None)
            _score = score
            i = -1
            
        self.ranking[i] = [avId, name, _score]
            
        if _score >= self.currentChallenge.getAmount():
            self.d_notifyWinner(avId, name)
            self.air.sendNetEvent('topToonsManager-UD-apply-%d' % self.air.getMsgSender(), [avId, self.getReward()])
            self.newChallenge(name)
            
        else:
            # Sort ranking
            self.ranking.sort(key=lambda x: x[2])
                
        self.d_updateData()
        self.save()
        
    def d_notifyWinner(self, doId, name):
        self.sendUpdateToChannel(10, 'notifyWinner', [name, doId])
        
    def __getName(self, avId):
        return self.air.friendsManager.getToonName(avId)

    def getReward(self):
        return self.currentChallenge.reward
        
    def __uploadLastMonth(self, data):
        self.notify.info('Sending last month result to site...')
        SiteUploadFSM(self, data)
        
    def waitForNextMonth(self):
        def _nm(task):
            self.__uploadLastMonth(self.__topToonsData)

            self.__curMonth = getCurrentMonth()
            self.__topToonsData = getEmptySiteToonsColl(self.__curMonth)
            
            self.waitForNextMonth()
            
            return task.done
            
        taskMgr.doMethodLater(timeToNextMonth() + 1, _nm, 'DistributedTopToonsManagerUD-nextMonth')
        
    def saveSite(self):
        if self.air.dbConnType == 'mongodb':        
            self.air.dbGlobalCursor.siteToons.update({'month': self.__curMonth}, {'$set': self.__topToonsData}, upsert=True)
        
    def __topToonsScore(self, avId, categories, score):
        def _add(cat):
            cd = self.__topToonsData[str(cat)]
            cd[str(avId)] = cd.get(str(avId), 0) + score
        
        start = TopToonsGlobals._CAT_BEGIN
        end = TopToonsGlobals._CAT_END
        while start <= end:
            if categories & start:
                _add(start)
                
            start *= 2
        
        self.saveSite()
        