import direct.directbase.DirectStart
from direct.actor.Actor import Actor
wall = loader.loadTexture("phase_6/maps/tt_central_fence.jpg")
environ = loader.loadModel("phase_5/models/cogdominium/tt_m_ara_cfg_propellerPack_large.bam")
environ.reparentTo(render)
environ.ls()
propeller = loader.loadModel("phase_5/models/cogdominium/tt_m_ara_cfg_toonPropeller.bam")
propeller.reparentTo(environ)
propeller.setP(-31)
propeller.setZ(0.7)
propeller.setY(0.465)
run()