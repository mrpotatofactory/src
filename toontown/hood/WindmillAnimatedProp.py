import AnimatedProp
from direct.actor import Actor
from direct.interval.IntervalGlobal import *

class WindmillAnimatedProp(AnimatedProp.AnimatedProp):

    def __init__(self, node):
        AnimatedProp.AnimatedProp.__init__(self, node)
        parent = node.getParent()
        self.windmill = Actor.Actor(node, copy=0)
        self.windmill.reparentTo(parent)
        self.windmill.loadAnims({'running': 'phase_14/models/props/windmill_chan-running'})
        self.windmill.pose('running', 0)
        self.windmill.setPosHpr(node, 0, 0, 0, 0, 0, 0)
        self.node = self.windmill

    def delete(self):
        AnimatedProp.AnimatedProp.delete(self)
        self.windmill.cleanup()
        del self.windmill
        del self.node

    def enter(self):
        AnimatedProp.AnimatedProp.enter(self)
        self.windmill.loop('running')

    def exit(self):
        AnimatedProp.AnimatedProp.exit(self)
        self.windmill.stop()
