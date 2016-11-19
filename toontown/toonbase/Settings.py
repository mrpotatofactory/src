import os

doc = '''
# This is the settings file. If you wish to edit it by hand, here's what you need to know:
# <- starts a comment
# config=value

# The value must be either "true" or "false"

# The valid configs are:

# acceptNewFriends (default true)
# acceptNonFriendWhispers (default true)
# enableMusic (default true)
# enableSFX (default true)
# enableChatSound (default true)
# enableShadows (default true)

'''

defaultDict = {
               'acceptNewFriends': 'true',
               'acceptNonFriendWhispers': 'true',
               'enableMusic': 'true',
               'enableSFX': 'true',
               'enableChatSound': 'true',
               'enableShadows': 'true',
              }
              
FILENAME = 'settings.txt'

configDict = defaultDict.copy()

def load():
    if not os.path.isfile(FILENAME):
        save()
        return
            
    with open(FILENAME, 'rb') as f:
        i = 0
        for line in f:
            i += 1
                
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
                    
            if '=' not in line:
                raise SyntaxError('Syntax error at line %d: %s' % (i, line))
                    
            config, value = line.split('=', 1)
            config = config.strip()
            value = value.strip()
            
            if config not in configDict:
                raise ValueError("Invalid config '%s' at line %d" % (config, i))
                    
            if value not in ('true', 'false'):
                raise ValueError("Invalid config value '%s' at line %d" % (value, i))
                    
            configDict[config] = (value == 'true')
        
def save():
    with open(FILENAME, 'wb') as f:
        f.write(doc)
        f.write('\n')
        for config, value in configDict.items():
            f.write('%s=%s\n' % (config, 'true' if value else 'false'))
        
def getAcceptingNewFriends():
    return configDict.get('acceptNewFriends', True)
        
def getAcceptingNonFriendWhispers():
    return configDict.get('acceptNonFriendWhispers', True)
    
def getEnableMusic():
    return configDict.get('enableMusic', True)
    
def getEnableSFX():
    return configDict.get('enableSFX', True)
    
def getEnableChatSound():
    return configDict.get('enableChatSound', True)
    
def getEnableShadows():
    return configDict.get('enableShadows', True)
    
def update(config, value):
    configDict[config] = value
    save()
