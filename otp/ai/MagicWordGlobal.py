from direct.showbase import PythonUtil

ACCESS_MOD = 300
ACCESS_DEV = 400
ACCESS_ADMIN = 500
ACCESS_TOP = 1000

MINIMUM_MAGICWORD_ACCESS = ACCESS_MOD

MW_DEV_ONLY = 1
MW_LIVE_ONLY = 2

class MagicError(Exception):
    pass

def ensureAccess(access, msg='Insufficient access'):
    if spellbook.getInvokerAccess() < access:
        raise MagicError(msg)

class Spellbook:
    isLive = config.GetBool('mw-is-live', False)
    
    def __init__(self):
        self.words = {}

        self.currentInvoker = None
        self.currentTarget = None

    def addWord(self, word):
        self.words[word.name] = word

    def process(self, invoker, target, incantation):
        self.currentInvoker = invoker
        self.currentTarget = target
        
        word, args = (incantation.split(' ', 1) + [''])[:2]

        try:
            return self.doWord(word, args)
            
        except MagicError as e:
            return e.message
            
        except Exception:
            return PythonUtil.describeException(backTrace=1)
            
        finally:
            self.currentInvoker = None
            self.currentTarget = None

    def doWord(self, wordName, args):
        word = self.words.get(wordName)
        if not word:
            return
            
        if Spellbook.isLive and word.flags & MW_DEV_ONLY:
            raise MagicError('Disabled on live server')

        ensureAccess(word.access)
        if self.getTarget() and self.getTarget() != self.getInvoker():
            if self.getInvokerAccess() <= self.getTarget().getAdminAccess():
                raise MagicError('Target must have lower access')
                
            ensureAccess(word.accessOther, 'This magic word requires higher access when applying to others')

        result = word.run(args)
        if result is not None:
            return str(result)

    def getInvoker(self):
        return self.currentInvoker

    def getTarget(self):
        return self.currentTarget

    def getInvokerAccess(self):
        if not self.currentInvoker:
            return 0
            
        return self.currentInvoker.getAdminAccess()
        
    def __repr__(self):
        r = ''
        accessToJob = {300: 'MOD', 400: 'DEV', 500: 'ADMIN', 1000: 'TOP ADMIN'}
        jobToWords = {}
        
        for name, word in self.words.items():
            access = word.access
            accessOther = word.accessOther
            job = accessToJob.get(access)
            if job is None:
                if access > 500:
                    job = accessToJob[1000]
                    
                else:
                    job = 'DEFAULT JOB'
                    
            flagsText = []
            if word.flags & MW_DEV_ONLY:
                flagsText.append('MW_DEV_ONLY')
               
            if word.flags & MW_LIVE_ONLY:
                flagsText.append('MW_LIVE_ONLY')
                
            if not flagsText:
                flagsText.append('0 <none>')
                
            chainsText = map(lambda x: x.name, word.chains)
            jobToWords.setdefault(job, []).append('%s\n  access: %d\n  accessOther: %d\n  flags: %s\n  chains: %s\n'
                                                  % (name, access, accessOther, ' | '.join(flagsText), ', '.join(chainsText)))
            
        jobs = sorted(jobToWords.keys())
        for job in jobs:
            r += '--------------------- %s ---------------------\n' % job
            for word in sorted(jobToWords[job]):
                r += word + '\n'
                
            r += '\n'
                
        return r[:-3]

spellbook = Spellbook()

class MagicWordChain:
    def __init__(self, name, defaultAccess, defaultFlags=0):
        self.name = name
        self.defaultAccess = defaultAccess
        self.defaultFlags = defaultFlags

CHAIN_DEFAULT = MagicWordChain('Default', ACCESS_DEV)
CHAIN_HEAD = MagicWordChain('God commands', ACCESS_TOP)
CHAIN_ADM = MagicWordChain('Administrator commands', ACCESS_ADMIN)
CHAIN_CHEAT = MagicWordChain('Game cheats', ACCESS_DEV)
CHAIN_CHARACTERSTATS = MagicWordChain('Character-stats cheats', ACCESS_DEV)
CHAIN_MOD = MagicWordChain('Moderation commands', ACCESS_MOD)
CHAIN_DISABLED_ON_LIVE = MagicWordChain('Disabled on live', 0, MW_DEV_ONLY)
CHAIN_DISABLED_ON_DEV = MagicWordChain('Disabled on dev', 0, MW_LIVE_ONLY)

class MagicWord:
    def __init__(self, name, func, types, access, accessOther, chains, flags, doc):
        self.name = name
        self.func = func
        self.types = types
        self.access = access
        self.accessOther = accessOther
        self.chains = chains
        self.flags = flags
        self.doc = doc

    def parseArgs(self, string):
        maxArgs = self.func.func_code.co_argcount
        minArgs = maxArgs - (len(self.func.func_defaults) if self.func.func_defaults else 0)

        args = string.split(None, maxArgs-1)[:maxArgs]
        if len(args) < minArgs:
            raise MagicError('Magic word %s requires at least %d arguments' % (self.name, minArgs))

        output = []
        for i, (type, arg) in enumerate(zip(self.types, args)):
            try:
                targ = type(arg)
            except (TypeError, ValueError):
                raise MagicError('Argument %d of magic word %s must be %s' % (i, self.name, type.__name__))

            output.append(targ)

        return output

    def run(self, rawArgs):
        args = self.parseArgs(rawArgs)
        return self.func(*args)


class MagicWordDecorator:
    def __init__(self, name=None, types=[str], access=None, accessOther=None, chains=[CHAIN_DEFAULT]):
        self.name = name
        self.types = types
        self.chains = chains
        
        if access is not None:
            self.access = access
            
        else:
            if len(chains) != 1:
                raise MagicError('magicWord: unable to determine accessLevel\nprovide exactly one chain or specify it explicitly')
            
            self.access = chains[0].defaultAccess
            
        if not self.access:
            self.access = CHAIN_DEFAULT.defaultAccess
            
        self.accessOther = self.access
        if accessOther is not None:
            if accessOther < self.access:
                raise MagicError('accessOther must be greater or equal to access')
                
            self.accessOther = accessOther
            
        self.flags = 0
        for chain in self.chains:
            self.flags |= chain.defaultFlags

    def __call__(self, mw):
        name = self.name
        if name is None:
            name = mw.func_name

        word = MagicWord(name, mw, self.types, self.access, self.accessOther, self.chains, self.flags, mw.__doc__)
        spellbook.addWord(word)

        return mw

magicWord = MagicWordDecorator
