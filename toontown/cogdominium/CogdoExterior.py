from direct.showbase.DirectObject import DirectObject

class CogdoExterior(DirectObject):
    
    def __init__(self, distributed):
        self.type = distributed.getFOType()