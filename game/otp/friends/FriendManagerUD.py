from direct.showbase.DirectObject import DirectObject
from direct.directnotify import DirectNotifyGlobal

import datetime
import string
import random

CHARS = string.ascii_lowercase + '0123456789'
TWO_DAYS = 2 * 60 * 60 * 24

class FriendManagerUD(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('FriendManagerUD')
    
    def __init__(self, air):
        self.air = air
        
        self.accept('TF_request_code', self.__requestCode)
        self.accept('TF_request_use', self.__requestUse)
        self.accept('TF_request', self.__doAdd)
        
        self.__loadCodes()
        
    def __loadCodes(self):
        if self.air.dbConnType == 'mongodb':
            self.codes = {x['avId']: x['codes'] for x in self.air.dbCursor.secrets.find()}
            
        else:
            self.notify.warning('Not using mongodb, self.codes will be non-persistent')
            self.codes = {}
            
    def __getCodesOf(self, avId):
        res = []
        now = datetime.datetime.now()
        
        for code in self.codes.get(avId, []):
            issued = code['issued']
            expired = (now - issued).total_seconds() > TWO_DAYS
            if not expired:
                res.append(code)
            
        self.__updateCodes(avId, res)            
        return res
            
    def __updateCodes(self, avId, codes):
        self.codes[avId] = codes
        if self.air.dbConnType == 'mongodb':
            codes = {'codes': codes, 'avId': avId}
            self.air.dbCursor.secrets.update({'avId': avId}, {'$set': codes}, upsert=True)
            
    def __getCodeAvId(self, needle, attempt=0):
        now = datetime.datetime.now()
        
        for avId, codes in self.codes.items():
            for code in codes:
                if code['code'] == needle:
                    issued = code['issued']
                    expired = (now - issued).total_seconds() > TWO_DAYS
                    if not expired:
                        return avId
            
        if not attempt:
            # Code not found. Reload DB and try again, but do this only once
            self.__loadCodes()
            return self.__getCodeAvId(needle, 1)
            
        return 0
            
    def __getPCC(self, avId):
        return self.air.csm.GetPuppetConnectionChannel(avId)
        
    def __requestCode(self, mgrDoId, avId):
        ccodes = self.__getCodesOf(avId)
        if len(ccodes) > 50:
            self.__sendRequestCodeRes(mgrDoId, avId, 0)
            return
            
        code = ''
        while not code or self.__getCodeAvId(code):
            p1 = ''.join(random.choice(CHARS) for _ in xrange(3))
            p2 = ''.join(random.choice(CHARS) for _ in xrange(3))
            code = p1 + ' ' + p2
            
        ccodes.append({'code': code, 'issued': datetime.datetime.now()})
        self.__updateCodes(avId, ccodes)
        self.__sendRequestCodeRes(mgrDoId, avId, 1, code)
        self.notify.info('Issued new code for %d: %s' % (avId, code))
        self.air.writeServerEvent('secret-code-issued', avId=avId, code=code)
        
    def __sendResponse(self, field, mgrDoId, avId, args):
        shardId = self.air.getMsgSender()
        field = self.air.dclassesByName['FriendManagerAI'].getFieldByName(field)
        dg = field.aiFormatUpdate(mgrDoId, self.__getPCC(avId), shardId, args)
        self.air.send(dg)
        
    def __sendRequestCodeRes(self, mgrDoId, avId, result, code=''):
        self.__sendResponse('requestSecretResponse', mgrDoId, avId, [result, code])
        
    def __requestUse(self, mgrDoId, avId, code):
        self.notify.info('%d is attempting to use %s' % (avId, code))
        target = self.__getCodeAvId(code)
        if not target:
            self.__sendResponse('submitSecretResponse', mgrDoId, avId, [0, 0])
            self.notify.info('Unknown code')
            return
            
        # Remove the code
        ccodes = self.__getCodesOf(target)
        nc = []
        for c in ccodes:
            if c['code'] != code:
                nc.append(c)
                
        self.__updateCodes(avId, nc)
            
        if target == avId:
            self.__sendResponse('submitSecretResponse', mgrDoId, avId, [3, 0])
            self.notify.info('Entered his own code!')
            return
            
        self.__doAdd(avId, target, mgrDoId, code)
            
    def __doAdd(self, avId, target, mgrDoId=0, code='__notset__'):
        self.notify.info('doAdd: %d %d %d %s' % (avId, target, mgrDoId, code))
        
        def _resp():
            if mgrDoId:
                self.__sendResponse('submitSecretResponse', mgrDoId, avId, [1, target])
            self.notify.info('Got resp from %d, target added to friend list!' % avId)
            self.air.writeServerEvent('secret-code-used', avId=avId, code=code, newFriend=target)
            
        # avId must be online
        self.air.sendNetEvent('TF_AIadd_%d' % avId, [target, True])
        self.acceptOnce('TF_AIadd_%d_res' % avId, _resp)
        
        # Check if target is online
        if target in self.air.friendsManager.onlineToons:
            # Yes, let their AI handle this
            self.air.sendNetEvent('TF_AIadd_%d' % target, [avId, False])
            
        else:
            # Nope, gotta edit database
            def handleQuery(dclass, fields):
                if dclass != self.air.dclassesByName['DistributedToonUD']:
                    return
                
                wasInOldList = 0
                oldFriendsList = list(fields['setFriendsList'][0])
                newFriendsList = []
                
                for fr in oldFriendsList:
                    if fr[0] == avId:
                        wasInOldList = 1
                        newFriendsList.append((avId, 1))
                        
                    else:
                        newFriendsList.append(fr)
                        
                if not wasInOldList:
                    newFriendsList.append((avId, 1))
                
                self.air.dbInterface.updateObject(self.air.dbId, target, self.air.dclassesByName['DistributedToonUD'],
                                                  {'setFriendsList' : [newFriendsList]})
                    
            self.air.dbInterface.queryObject(self.air.dbId, target, handleQuery)
        