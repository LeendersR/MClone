def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


def discretize(position):
    x, y, z = position
    x, y, z = int(round(x)), int(round(y)), int(round(z))
    return x, y, z
