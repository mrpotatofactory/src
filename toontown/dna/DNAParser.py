from pandac.PandaModules import *

from libpandadna import *

def loadDNAFile(*a, **kw):
    return loader.loadDNAFile(*a, **kw)
        
def setupDoor(a, b, c, d, e, f):
    try:
        e = int(str(e).split('_')[0])
        
    except:
        print 'setupDoor: error parsing', e
        e = 9999
        
    DNADoor.setupDoor(a, b, c, d, e, f)
