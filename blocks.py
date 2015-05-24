class Block(object):
    name = "UNKNOWN"
    top_texture = (0, 0)
    bottom_texture = (0, 0)
    side_texture = (0, 0)

    def __init__(self):
        top = self.texture_coords(*self.top_texture)
        bottom = self.texture_coords(*self.bottom_texture)
        side = self.texture_coords(*self.side_texture)
        self.texture_data = top + bottom + side*4

    @staticmethod
    def texture_coords(x, y, size=0.25):
        x *= size
        y *= size
        bottom_left = [x, y]
        bottom_right = [x+size, y]
        top_right = [x+size, y+size]
        top_left = [x, y+size]
        return bottom_left + bottom_right + top_right + top_left

    @staticmethod
    def cube_vertices(x, y, z, size=0.5):
        # Order: top, bottom, left, right, front, back
        # t=top, b=bottom, l=left, r=right, b=back, f=front
        tlb = [x-size, y+size, z-size]
        tlf = [x-size, y+size, z+size]
        trf = [x+size, y+size, z+size]
        trb = [x+size, y+size, z-size]
        blb = [x-size, y-size, z-size]
        brb = [x+size, y-size, z-size]
        brf = [x+size, y-size, z+size]
        blf = [x-size, y-size, z+size]
        return (tlb + tlf + trf + trb +
                blb + brb + brf + blf +
                blb + blf + tlf + tlb +
                brf + brb + trb + trf +
                blf + brf + trf + tlf +
                brb + blb + tlb + trb)


class GrassBlock(Block):
    name = 'Grass'
    top_texture = (1, 0)
    bottom_texture = (0, 1)
    side_texture = (0, 0)


class SandBlock(Block):
    name = 'Sand'
    top_texture = (1, 1)
    bottom_texture = (1, 1)
    side_texture = (1, 1)


class StoneBlock(Block):
    name = 'Stone'
    top_texture = (2, 1)
    bottom_texture = (2, 1)
    side_texture = (2, 1)


class BrickBlock(Block):
    name = 'Brick'
    top_texture = (2, 0)
    bottom_texture = (2, 0)
    side_texture = (2, 0)
