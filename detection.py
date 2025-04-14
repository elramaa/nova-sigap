import numpy as np

def is_stationary(positions, duration_threshold=15, movement_threshold=30):
    if len(positions) < 2:
        return False

    times = [pos[2] for pos in positions]
    if times[-1] - times[0] < duration_threshold:
        return False

    coords = np.array([[p[0], p[1]] for p in positions])
    movement = np.linalg.norm(coords[-1] - coords[0])

    return movement < movement_threshold
