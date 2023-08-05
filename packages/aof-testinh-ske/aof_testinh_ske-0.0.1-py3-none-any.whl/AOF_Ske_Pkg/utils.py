import math
import numpy as np

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def sample_sphere_2D(number_of_samples):
    sphere_points = np.zeros((number_of_samples, 2))
    alpha = (2 * math.pi) / number_of_samples
    
    for i in range(number_of_samples):
        sphere_points[i][0] = math.cos(alpha * (i - 1))
        sphere_points[i][1] = math.sin(alpha * (i - 1))
    return sphere_points
