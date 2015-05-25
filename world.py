import random
import time
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet import image
from collections import deque
from blocks import *
from utils import discretize


class World(object):
    def __init__(self):
        self.CHUNK_SIZE = 16
        self.batch = pyglet.graphics.Batch()
        self.group = TextureGroup(image.load('texture.png').get_texture())
        self.blocks = {}
        self.drawn_blocks = {}
        self.vertex_lists = {}
        self.chunks = {}
        self.current_chunk = (float('inf'), float('inf'), float('inf'))
        self.drawing_queue = deque()
        self.generate_world()

    def neighbors(self, position):
        for axis in xrange(3):
            for direction in [-1, 1]:
                new_pos = list(position)
                new_pos[axis] += direction
                yield tuple(new_pos)

    def exposed(self, position):
        for neighbor in self.neighbors(position):
            if neighbor not in self.blocks:
                    return True
        return False

    def add_block(self, position, block_type, urgent=True):
        if position in self.blocks:
            self.remove_block(position)
        self.blocks[position] = block_type
        self.chunks.setdefault(self.chunk_position(position),
                               []).append(position)
        if urgent:
            if self.exposed(position):
                self.draw_block(position)
            self.redraw_neighbors(position)

    def remove_block(self, position, urgent=True):
        if position not in self.blocks:
            return
        del self.blocks[position]
        self.chunks[self.chunk_position(position)].remove(position)
        if urgent:
            if position in self.drawn_blocks:
                self.undraw_block(position)
            self.redraw_neighbors(position)

    def draw_chunk(self, chunk):
        for position in self.chunks.get(chunk, []):
            if position not in self.drawn_blocks and self.exposed(position):
                self.draw_block(position, False)

    def undraw_chunk(self, chunk):
        for position in self.chunks.get(chunk, []):
            if position in self.drawn_blocks:
                self.undraw_block(position, False)

    def change_chunk(self, new_chunk):
        old_chunks_visible = set()
        new_chunks_visible = set()
        num_adjacent = 2
        for dx in xrange(-num_adjacent, num_adjacent + 1):
            for dy in xrange(-num_adjacent, num_adjacent + 1):
                for dz in xrange(-num_adjacent, num_adjacent + 1):
                    x, y, z = self.current_chunk
                    old_chunks_visible.add((x + dx, y + dy, z + dz))
                    x, y, z = new_chunk
                    new_chunks_visible.add((x + dx, y + dy, z + dz))
        draw = new_chunks_visible - old_chunks_visible
        undraw = old_chunks_visible - new_chunks_visible
        for chunk in draw:
            self.draw_chunk(chunk)
        for chunk in undraw:
            self.undraw_chunk(chunk)
        self.current_chunk = new_chunk

    def load_chunks(self, position):
        new_chunk = self.chunk_position(position)
        if self.current_chunk != new_chunk:
            self.change_chunk(new_chunk)

    def redraw_neighbors(self, position):
        for neighbor in self.neighbors(position):
            if neighbor not in self.blocks:
                continue
            if neighbor in self.drawn_blocks:
                if not self.exposed(neighbor):
                    self.undraw_block(neighbor)
            else:
                if self.exposed(neighbor):
                    self.draw_block(neighbor)

    def draw_block(self, position, urgent=True):
        self.drawn_blocks[position] = self.blocks[position]
        if urgent:
            self._draw_block(position)
        else:
            self.drawing_queue.append((self._draw_block, position))

    def _draw_block(self, position):
        """ Draw block at `position`"""
        block = self.blocks.get(position, None)
        if not block or position in self.vertex_lists:
            return
        vertices = Block.cube_vertices(*position)
        texture = block.texture_data
        vertex_list = self.batch.add(24, GL_QUADS, self.group,
                                     ('v3f/static', vertices),
                                     ('t2f/static', texture))
        self.vertex_lists[position] = vertex_list

    def undraw_block(self, position, urgent=True):
        del self.drawn_blocks[position]
        if urgent:
            self._undraw_block(position)
        else:
            self.drawing_queue.append((self._undraw_block, position))

    def _undraw_block(self, position):
        if position in self.vertex_lists:
            self.vertex_lists.pop(position).delete()

    def draw(self):
        self.batch.draw()

    def update(self, dt):
        start = time.clock()
        while self.drawing_queue and time.clock()-start < dt:
            func, position = self.drawing_queue.popleft()
            func(position)

    def collides(self, obj):
        position = list(obj.position)
        height = obj.height
        max_overlap = 0.1
        disc_pos = discretize(position)
        for axis in xrange(3):
            for direction in [-1, 1]:
                overlap = (position[axis] - disc_pos[axis]) * direction
                if overlap < max_overlap:
                    continue
                for dy in xrange(height):
                    new_pos = list(disc_pos)
                    new_pos[axis] += direction
                    new_pos[1] -= dy
                    if tuple(new_pos) in self.blocks:
                        position[axis] -= (overlap - max_overlap) * direction
                        break
        return tuple(position)

    def occupied(self, position):
        return discretize(position) in self.blocks

    def generate_world(self, seed=None):
        if seed is None:
            seed = time.clock()
        random.seed(seed)
        size = 20
        for x in xrange(-size, size):
            for z in xrange(-size, size):
                self.add_block((x, -2, z), GrassBlock(), urgent=False)

        self.add_block((3, -1, 3), StoneBlock(), urgent=False)
        self.add_block((4, 0, 3), BrickBlock(), urgent=False)
        self.add_block((5, 1, 3), GrassBlock(), urgent=False)
        self.add_block((6, 2, 3), SandBlock(), urgent=False)

    def chunk_position(self, position):
        x, y, z = discretize(position)
        return x/self.CHUNK_SIZE, y/self.CHUNK_SIZE, z/self.CHUNK_SIZE
