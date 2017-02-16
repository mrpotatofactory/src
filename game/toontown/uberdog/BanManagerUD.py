from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify import DirectNotifyGlobal
import urllib, urllib2, json, hashlib

class BanManagerUD(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerUD')
    BanUrl = config.GetString('ban-base-url', 'http://toontownnext.net/api/ban/')
    DoActualBan = config.GetBool('ban-do-ban', False)
    
    def __init__(self, air):
        self.air = air
        self.accept('BANMGR_ban', self.banUD)
            
    def banUD(self, banner, avId, accountId, time, banReason):
        self.air.csm.getUsername(accountId, lambda username: self.__ban(username, avId, accountId, banner, time, banReason))
        
    def __ban(self, username, avId, accountId, banner, time, banReason):     
        headers = {'User-Agent' : 'TTBanManager'}
        
        bannerLevel = self.air.friendsManager.getToonAccess(banner)
        bannerName = self.air.friendsManager.getToonName(banner)
            
        innerData = json.dumps({'username': username, 'reason': banReason,
                                'banner': '%s (%s): %s' % (bannerName, banner, bannerLevel),
                                'duration': time})
        hmac = hashlib.sha512(innerData + self.air.getApiKey()).hexdigest()
        
        data = 'data=%s' % urllib.quote(innerData)
        data += '&hmac=%s' % urllib.quote(hmac)
        
        if self.DoActualBan:
            try:
                req = urllib2.Request(self.BanUrl, data, headers)
                res = json.loads(urllib2.urlopen(req).read())
                success = res['success']
                error = res.get('error')
            
            except Exception as e:                
                success = False
                error = str(e)

        else:
            success = True
            
        if not success:
            # Better notify the banner
            avId = self.air.csm.GetPuppetConnectionChannel(banner)
            msg = 'Failed to ban %s: %s' % (username, error)
            self.air.sendSysMsg('BanManagerUD: ERROR: %s' % msg, avId)
            self.notify.warning(msg)
            return
                
        dg = PyDatagram()
        dg.addServerHeader(self.air.csm.GetPuppetConnectionChannel(avId), self.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(152)
        dg.addString('You were banned by a moderator!')
        self.air.send(dg)

        self.notify.info('%s (%d/%d) banned %s for %s hours: %s' % (bannerName, banner, bannerLevel, username, time, banReason))
        self.air.writeServerEvent('banned', accountId, username=username, banner='%s (%d/%d)' % (bannerName, banner, bannerLevel),
                                  time=time, reason=banReason)
                
        for doId, access in self.air.friendsManager.toon2data.items():
            access = access.get('access', 0)
            if access >= bannerLevel:
                self.sendToAv(self.air.csm.GetPuppetConnectionChannel(doId),
                              '%s (%d): %d' % (bannerName, banner, bannerLevel),
                              username, time, banReason)
                                
    def sendToAv(self, avId, *values):
        msg = '%s banned %s for %s hours: %s' % values
        self.air.sendSysMsg(msg, avId)
