import numpy as np

# Threshold for valid keypoint confidence
MIN_CONFIDENCE = 0.3

def valid(pt):
    return pt is not None and len(pt) == 3 and pt[2] > MIN_CONFIDENCE

def distance(p1, p2):
    return np.linalg.norm(np.array(p1[:2]) - np.array(p2[:2]))

def average_y(*points):
    return np.mean([p[1] for p in points if valid(p)])

def is_crouching(keypoints):
    if len(keypoints) < 17:
        return False

    l_hip, r_hip = keypoints[11], keypoints[12]
    l_knee, r_knee = keypoints[13], keypoints[14]
    l_ankle, r_ankle = keypoints[15], keypoints[16]

    if not all(map(valid, [l_hip, r_hip, l_knee, r_knee, l_ankle, r_ankle])):
        return False

    hip = np.mean([l_hip[:2], r_hip[:2]], axis=0)
    knee = np.mean([l_knee[:2], r_knee[:2]], axis=0)
    ankle = np.mean([l_ankle[:2], r_ankle[:2]], axis=0)

    leg_length = distance(hip, ankle)
    hip_to_knee = distance(hip, knee)

    if leg_length == 0:
        return False

    ratio = hip_to_knee / leg_length
    return ratio < 0.45

def is_fighting_pose(keypoints):
    try:
        l_shoulder, r_shoulder = keypoints[5], keypoints[6]
        l_elbow, r_elbow = keypoints[7], keypoints[8]
        l_wrist, r_wrist = keypoints[9], keypoints[10]
        if l_elbow[1] < l_shoulder[1] or r_elbow[1] < r_shoulder[1]:
            return True
    except:
        pass
