import numpy as np

def euclidean_distance(ptA, ptB):
    return np.linalg.norm(np.array(ptA) - np.array(ptB))

def rect_to_bb(rect):
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    return (x, y, w, h)

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def resize_frame(frame, width=420):
    (h, w) = frame.shape[:2]
    r = width / float(w)
    dim = (width, int(h * r))
    import cv2
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
