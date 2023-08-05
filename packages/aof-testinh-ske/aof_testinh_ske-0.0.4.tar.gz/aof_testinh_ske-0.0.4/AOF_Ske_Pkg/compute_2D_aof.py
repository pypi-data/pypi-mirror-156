import math
import numpy as np

def compute_2D_aof(distImage, IDX, sphere_points, epsilon, number_of_samples):
    m = distImage.shape[0]
    n = distImage.shape[1]
    normals = np.zeros(sphere_points.shape)
    flux_img = np.zeros((m, n))
    
    for t in range(0, number_of_samples):
        normals[t] = sphere_points[t]
    
    sphere_points = sphere_points * epsilon
    
    XInds = IDX[0]
    YInds = IDX[1]
    
    for i in range(0, m):
   
        for j in range(0, n):
            flux_value = 0
            if(distImage[i][j] > -1.5):
                if(i > epsilon and j > epsilon and i < m-epsilon and j < n-epsilon):
                    for ind in range(0, number_of_samples):
                        px = i+sphere_points[ind][0]+0.5
                        py = j+sphere_points[ind][1]+0.5
                        
                        cI = math.floor(i+sphere_points[ind][0]+0.5)
                        cJ = math.floor(j+sphere_points[ind][1]+0.5)
                        
                        bx = XInds[cI][cJ]
                        by = YInds[cI][cJ]
                        qq = [bx-px,by-py]
                        d = np.linalg.norm(qq)
                        if (d != 0):
                            qq = qq / d
                        else:
                            qq = [0, 0]
                        flux_value = flux_value + np.dot(qq, normals[ind])
            flux_img[i][j] = flux_value
    return flux_img
