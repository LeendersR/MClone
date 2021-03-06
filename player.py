import math
from pyglet.window import key, mouse
from utils import clamp
from blocks import GrassBlock


class Player(object):
    """Represents a player.

    Attributes:
        height: The height of the player.
        velocity: Its current velocity in for each axis.
        rotation: Its rotation on the x and y axis.
        rotation_speed: The speed with which the player rotates.
        position: The current position of the player.
        active_block: The current active block. The active block is the block
            which is placed when the player rightclicks.
    """
    def __init__(self, position=(0, 0, 0)):
        self.height = 2  # Height in number of blocks
        self.velocity = [0, 0, 0]
        self.rotation = (0, 0)
        self.rotation_speed = 0.25
        self.position = position
        self.active_block = GrassBlock()

    def camera_direction(self):
        """Gets a vector in which the player is looking
        """
        x_rot, y_rot = self.rotation
        m = math.cos(math.radians(y_rot))
        x = math.cos(math.radians(x_rot-90)) * m
        y = math.sin(math.radians(y_rot))
        z = math.sin(math.radians(x_rot-90)) * m
        return x, y, z

    def update_position(self, dt):
        """Updates the position of the player.
        """
        x_vel, y_vel, z_vel = self.velocity
        if not (x_vel or z_vel):
            return
        x_rot, y_rot = self.rotation
        angle = math.degrees(math.atan2(x_vel, z_vel))
        x_angle = math.radians(x_rot + angle)
        y_angle = math.radians(y_rot)
        dx = dt*math.cos(x_angle)
        dz = dt*math.sin(x_angle)
        x, y, z = self.position
        self.position = (x+dx, y, z+dz)

    def update(self, dt):
        self.update_position(dt)

    def on_key_press(self, pressed_key, modifiers):
        """Increase velocity on keypress.
        """
        if pressed_key == key.W:
            self.velocity[0] -= 1
        elif pressed_key == key.S:
            self.velocity[0] += 1
        elif pressed_key == key.A:
            self.velocity[2] -= 1
        elif pressed_key == key.D:
            self.velocity[2] += 1
        elif pressed_key == key.SPACE:
            if self.velocity[1] == 0:
                self.velocity[1] = 1.0

    def on_key_release(self, pressed_key, modifiers):
        """Decrease velocity on key release.
        """
        if pressed_key == key.W:
            self.velocity[0] += 1
        elif pressed_key == key.S:
            self.velocity[0] -= 1
        elif pressed_key == key.A:
            self.velocity[2] += 1
        elif pressed_key == key.D:
            self.velocity[2] -= 1

    def on_mouse_motion(self, x, y, dx, dy):
        """Change the rotation of the player when the mouse moves.
        """
        x, y = self.rotation
        x, y = x + dx * self.rotation_speed, y + dy * self.rotation_speed
        y = clamp(-90, y, 90)
        self.rotation = (x, y)
