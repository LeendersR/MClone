import math
import random


def noise(x, y, z):
    """ Ported from http://mrl.nyu.edu/~perlin/noise/ (yes it is a mess)
    """
    X = int(x % 255)
    Y = int(y % 255)
    Z = int(z % 255)
    x = x - int(x)
    y = y - int(y)
    z = z - int(z)
    u = fade(x)
    v = fade(y)
    w = fade(z)

    A = p[X]+Y
    AA = p[A]+Z
    AB = p[A+1]+Z
    B = p[X+1]+Y
    BA = p[B]+Z
    BB = p[B+1]+Z

    # Again yes it is a mess but pep8 compliant?
    return lerp(w, lerp(v, lerp(u, grad(p[AA], x, y, z),
                                grad(p[BA], x-1, y, z)),
                        lerp(u, grad(p[AB], x, y-1, z),
                             grad(p[BB], x-1, y-1, z))),
                lerp(v, lerp(u, grad(p[AA+1], x, y, z-1),
                             grad(p[BA+1], x-1, y, z-1)),
                lerp(u, grad(p[AB+1], x, y-1, z-1),
                     grad(p[BB+1], x-1, y-1, z-1))))


def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(t, a, b):
    return a + t * (b - a)


def grad(hash, x, y, z):
    h = hash % 16
    u = x if h < 8 else y
    v = y if h < 4 else (x if h == 12 or h == 14 else z)
    r = u if h % 2 == 0 else -u
    r += v if h % 4 == 0 else -v
    return r

p = 2*[151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225,
       140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247,
       120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57,
       177, 33, 88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175,
       74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229,
       122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102,
       143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208,
       89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198,
       173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118,
       126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189,
       28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221,
       153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110,
       79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242,
       193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14,
       239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176,
       115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222, 114, 67,
       29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180]


def fbm(x, y, z, octaves=8, lacunarity=2.0, gain=0.5):
    amplitude = 1.0
    frequency = 1.0
    accum = 0.0
    for i in range(octaves):
        accum += amplitude * noise(x * frequency, y * frequency, z * frequency)
        amplitude *= gain
        frequency *= lacunarity
    return accum


def gen_map(offset, chunk_size, base_level, map_height):
    blocks = set()
    smoothness = float(random.randint(15, 30))
    dx, dy, dz = offset
    for x in xrange(dx, dx+chunk_size):
        for z in xrange(dz, dz+chunk_size):
            for y in xrange(map_height):
                density = fbm(x/smoothness, y/smoothness, z/smoothness)
                if y > base_level:
                    if density*10 > 0:
                        blocks.add((x, y, z))
                else:
                    blocks.add((x, y, z))
    return blocks