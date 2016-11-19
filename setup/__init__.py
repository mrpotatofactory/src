import sys, os

if __name__ == '__main__':
    print 'Do not run this file directly.'
    raise SystemExit(__import__('time').sleep(5000))
    
import direct
PATH = direct.__path__[0]

DIST_PATH = os.path.join(PATH, 'distributed')

def check(target, newstr, safe = 1):
    if safe:
        if not os.path.isfile(target):
            print 'You are not running from Astron Panda3D!'
            sys.exit()
    
    try:
        with open(target, 'rb') as f:
            tdata = f.read()
        
    except:
        tdata = ''
        
    newstr = newstr.lstrip('\n')
    
    if tdata != newstr:
        print 'Updating', target
        with open(target, 'wb') as f:
            f.write(newstr)
    
check(os.path.join(DIST_PATH, 'AstronInternalRepository.py'), open('setup/AstronInternalRepository.correct', 'rb').read())
check(os.path.join(DIST_PATH, 'AstronDatabaseInterface.py'), open('setup/AstronDatabaseInterface.correct', 'rb').read())
check(os.path.join(DIST_PATH, 'MsgTypes.py'), open('setup/MsgTypes.correct', 'rb').read())
check(os.path.join(PATH, 'showbase', 'LerpBlendHelpers.py'), open('setup/LerpBlendHelpers.correct', 'rb').read(), safe = 0)
check(os.path.join(PATH, 'showbase', 'PythonUtil.py'), open('setup/PythonUtil.correct', 'rb').read())
check(os.path.join(PATH, 'showbase', 'SfxPlayer.py'), open('setup/SfxPlayer.correct', 'rb').read())
check(os.path.join(PATH, 'distributed', 'NetMessenger.py'), open('setup/NetMessenger.correct', 'rb').read())

def makedir(dir):
    try:
        os.makedirs(dir)
   
    except Exception as e:        
        assert os.path.isdir(dir)
    
makedir('./databases/astrondb')
