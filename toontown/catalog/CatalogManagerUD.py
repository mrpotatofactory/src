from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from toontown.catalog import CatalogItem, CatalogItemList

class CatalogManagerUD(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('CatalogManagerUD')
    
    def __init__(self, air):
        self.air = air
        
        self.accept('CATALOG_addGift_AI2UD', self.__handleCatalogAddGift)
        
    def __handleCatalogAddGift(self, avId, blob):
        if avId in self.air.friendsManager.onlineToons:
            # Avatar is online, let its AI handle it (let's fucking hope he's not about to gtfo)
            self.air.sendNetEvent('CATALOG_addGift_UD2Toon_%d' % avId, [blob])
            self.notify.info('%d is online, gift deliver order sent to AI' % avId)
            return
            
        # Shit, gotta fuck with the db!
        self.air.dbInterface.queryObject(self.air.dbId, avId, lambda a, b: self.__handleRetrieve(a, b, avId, blob))
        
    def __handleRetrieve(self, dclass, fields, avId, blob):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.notify.warning('Unable to deliver gift: avId is not a DistributedToonUD!')
            return
          
        store = CatalogItem.Customization | CatalogItem.DeliveryDate | CatalogItem.GiftTag
        giftOnOrder = CatalogItemList.CatalogItemList(fields.get('setGiftSchedule', [''])[0], store=store)
        giftOnOrder.append(CatalogItem.getItem(blob, store=store))
        fields['setGiftSchedule'] = (giftOnOrder.getBlob(store=store),)
        
        self.air.dbInterface.updateObject(self.air.dbId, avId, self.air.dclassesByName['DistributedToonUD'], fields)
        self.notify.info('Successfully delivered gift to %d' % avId)
        