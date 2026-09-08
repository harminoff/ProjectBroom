"""Original reddish-brown primate fur and bare face. CC-BY-SA-4.0."""
from .jackal_materials import texture_bytes as fur_texture
SKIN='graphics/BRGMONKY.png'
def texture_bytes():
    return fur_texture({'fur':(111,57,39),'tail':(107,53,37),'ear':(125,76,62),
                        'paw':(155,104,81),'eye':(13,9,7),'claw':(214,195,153),
                        'whisker':(139,145,150)},back_shading=False)
