import pyglet
import math
from world import World
from player import Player
from pyglet.gl import *
from pyglet.window import key, mouse


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
        self.clear()
        self.set_exclusive_mouse(True)
        pyglet.clock.schedule_interval(self.update, 1.0/self.FRAMES_PER_SEC)

    def setup_opengl(self):
        glEnable(GL_CULL_FACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*self.SKY_COLOR))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, self.FOG_START)
        glFogf(GL_FOG_END, self.FOG_END)

    def clear(self):
        super(Game, self).clear()
        glClearColor(*self.SKY_COLOR)

    def set_exclusive_mouse(self, exclusive):
        super(Game, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def setup_3d(self):
        glEnable(GL_DEPTH_TEST)
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

    def on_draw(self):
        self.clear()
        self.setup_3d()
        self.world.draw()

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
            self.player.position = new_pos

    def on_key_press(self, pressed_key, modifiers):
        self.player.on_key_press(pressed_key, modifiers)
        if pressed_key == key.ESCAPE:
            self.set_exclusive_mouse(False)

    def on_key_release(self, pressed_key, modifiers):
        self.player.on_key_release(pressed_key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            self.player.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.exclusive:
            self.set_exclusive_mouse(True)


if __name__ == '__main__':
    game = Game()
    pyglet.app.run()
