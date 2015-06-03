class Block(object):
    """Represents a block in the world

    Attributes:
        name: The name of the block.
        top_texture: The (row, column) indices of the texture shown on the top.
        bottom_texture: The (row, column) indices of the texture shown on the
            bottom.
        side_texture: The (row, column) indices of the texture shown on each
            side of the cube.
        texture_data: The texture data that is send to the vertex buffer, this
            attribute is generated based on the above three attributes.
    """
    name = "UNKNOWN"
    top_texture = (0, 0)
    bottom_texture = (0, 0)
    side_texture = (0, 0)
    texture_data = []

    def __init__(self):
        if not self.texture_data:
            top = self.texture_coords(*self.top_texture)
            bottom = self.texture_coords(*self.bottom_texture)
            side = self.texture_coords(*self.side_texture)
            self.texture_data.extend(top + bottom + side*4)

    @staticmethod
    def texture_coords(row, column, size=0.25):
        """Returns texture coordinates for a given row, column and size.

        Args:
            row: The row in the texture.
            column: The column in the texture.
            size: The size of the texture.

        Returns:
            A list of coordinates containing the bottom left, bottom right,
            top right and top left coordinates.
        """
        x = row * size
        y = column * size
        bottom_left = [x, y]
        bottom_right = [x+size, y]
        top_right = [x+size, y+size]
        top_left = [x, y+size]
        return bottom_left + bottom_right + top_right + top_left

    @staticmethod
    def cube_vertices(x, y, z, size=0.5):
        """Returns coordinates for a cube

        Args:
            x: x position of the cube
            y: y position of the cube
            z: z position of the cube
            size: size of the cube

        Returns:
            A tuple of coordinates that represents all corner points of the
            cube.
        """
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
    texture_data = []


class SandBlock(Block):
    name = 'Sand'
    top_texture = (1, 1)
    bottom_texture = (1, 1)
    side_texture = (1, 1)
    texture_data = []


class StoneBlock(Block):
    name = 'Stone'
    top_texture = (2, 1)
    bottom_texture = (2, 1)
    side_texture = (2, 1)
    texture_data = []


class BrickBlock(Block):
    name = 'Brick'
    top_texture = (2, 0)
    bottom_texture = (2, 0)
    side_texture = (2, 0)
    texture_data = []
