import pyglet
import math
from world import World
from player import Player
from utils import discretize
from pyglet.gl import *
from pyglet.window import key, mouse
from pyglet.graphics import vertex_list


class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.FRAMES_PER_SEC = 60
        self.TERMINAL_VELOCITY = 10.0
        self.GAME_SPEED = 4.0
        self.SKY_COLOR = (135/255.0, 206/255.0, 235/255.0, 1.0)
        self.FOG_START = 20.0
        self.FOG_END = 60.0
        self.FOV = 65.0
        self.GRAVITY = 0.5
        self.exclusive = False
        self.world = World()
        self.player = Player()
        self.world.load_chunks(self.player.position)
        self.setup_opengl()
        self.setup_crosshair()
        self.clear()
        self.set_exclusive_mouse(True)
        pyglet.clock.schedule_interval(self.update, 1.0/self.FRAMES_PER_SEC)

    def setup_opengl(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*self.SKY_COLOR))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, self.FOG_START)
        glFogf(GL_FOG_END, self.FOG_END)

    def setup_crosshair(self):
        width, height = self.get_size()
        size = 10
        x = width/2
        y = height/2
        self.crosshair = vertex_list(4, ('v2i', (x - size, y, x + size, y, x,
                                                 y - size, x, y + size)))

    def clear(self):
        super(Game, self).clear()
        glClearColor(*self.SKY_COLOR)
        glColor3d(1, 1, 1)

    def set_exclusive_mouse(self, exclusive):
        super(Game, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def setup_3d(self):
        width, height = self.get_size()
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.FOV, width / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        # Invert it otherwise moving up means looking down
        glRotatef(y, -math.cos(math.radians(x)), 0, -math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    def setup_2d(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = self.get_size()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw_crosshair(self):
        glColor3d(0.25, 0.25, 0.25)
        self.crosshair.draw(GL_LINES)

    def on_draw(self):
        self.clear()
        self.setup_3d()
        self.world.draw()
        self.setup_2d()
        self.draw_crosshair()

    def apply_gravity(self, obj, dt):
        x_vel, y_vel, z_vel = obj.velocity
        y_vel -= dt * self.GRAVITY
        y_vel = max(y_vel, -self.TERMINAL_VELOCITY)
        dy = dt*y_vel
        obj.velocity = [x_vel, y_vel, z_vel]
        x, y, z = obj.position
        obj.position = (x, y+dy, z)

    def update(self, dt):
        self.world.update(1.0/self.FRAMES_PER_SEC)
        self.world.load_chunks(self.player.position)
        # We move a tiny amount each time, otherwise it would be possible
        # to fall through the blocks, because the system notices it too late
        num_steps = 10
        dt *= self.GAME_SPEED / float(num_steps)
        for step in range(num_steps):
            self.player.update(dt)
            self.apply_gravity(self.player, dt)
            new_pos = self.world.collides(self.player)
            # new_pos contains the nearest position without collisions
            # If we collided on the y-axis stop gravity
            if new_pos[1] != self.player.position[1]:
                self.player.velocity[1] = 0
            self.player.position = new_pos

    def hit_test(self, position, direction, max_distance=5):
        x, y, z = position
        x_dir, y_dir, z_dir = direction
        num_steps = 10
        x_step = x_dir/num_steps
        y_step = y_dir/num_steps
        z_step = z_dir/num_steps
        prev_pos = None
        for step in xrange(num_steps*max_distance):
            block_pos = discretize((x, y, z))
            if prev_pos != block_pos and self.world.occupied(block_pos):
                return prev_pos, block_pos
            prev_pos = block_pos
            x, y, z = x+x_step, y+y_step, z+z_step
        return None, None

    def position_intersects_object(self, position, obj):
        x, y, z = discretize(obj.position)
        for dy in xrange(obj.height):
            if position == (x, y-dy, z):
                return True
        return False

    def on_key_press(self, pressed_key, modifiers):
        self.player.on_key_press(pressed_key, modifiers)
        if pressed_key == key.ESCAPE:
            self.set_exclusive_mouse(False)

    def on_key_release(self, pressed_key, modifiers):
        self.player.on_key_release(pressed_key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            self.player.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.exclusive:
            self.set_exclusive_mouse(True)
        else:
            direction = self.player.camera_direction()
            prev_block_pos, block_pos = self.hit_test(self.player.position,
                                                      direction)
            if not block_pos:
                return
            if button == mouse.LEFT:
                self.world.remove_block(block_pos)
            elif button == mouse.RIGHT:
                if not self.position_intersects_object(prev_block_pos,
                                                       self.player):
                    self.world.add_block(prev_block_pos,
                                         self.player.active_block)


if __name__ == '__main__':
    game = Game()
    pyglet.app.run()
