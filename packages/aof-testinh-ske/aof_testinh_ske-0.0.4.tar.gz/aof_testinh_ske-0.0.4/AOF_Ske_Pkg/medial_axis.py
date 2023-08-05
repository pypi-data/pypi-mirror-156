from turtle import title
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from AOF_Ske_Pkg.compute_2D_aof import compute_2D_aof
from AOF_Ske_Pkg.distance_transform import get_distance_transform
from AOF_Ske_Pkg.utils import sample_sphere_2D

import cv2

def medial_axis(img_path, threshold, option):
    #using cv2 and Otsu's method
    img=cv2.imread(img_path)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, img_otsu = cv2.threshold(img_gray, 128, 255, cv2.THRESH_OTSU)
    img_bool = img_otsu<=th
    img_bool_re = img_otsu>th
   
    dist_img, idx = get_distance_transform(img_bool)
    dist_img_re, idx_re = get_distance_transform(img_bool_re)
    dist_full=dist_img+dist_img_re

    number_of_samples = 60
    epsilon = 1 
    flux_threshold = 18
    flux_threshold = threshold*number_of_samples

    sphere_points = sample_sphere_2D(number_of_samples)

    if(option == 'interior'):
        flux_img = compute_2D_aof(dist_img, idx, sphere_points, epsilon, number_of_samples)
        img_skelenton=flux_img>flux_threshold
        return(flux_img,dist_img,img_skelenton)
    elif (option=="exterior"):
        flux_img_re = compute_2D_aof(dist_img_re, idx_re, sphere_points, epsilon, number_of_samples)
        img_skelenton_re=flux_img_re>flux_threshold
        return(flux_img_re,dist_img_re,img_skelenton_re)
    elif (option=="full"):
        flux_img = compute_2D_aof(dist_img_re, idx_re, sphere_points, epsilon, number_of_samples)
        img_skelenton=flux_img>flux_threshold
        flux_img_re = compute_2D_aof(dist_img, idx, sphere_points, epsilon, number_of_samples)
        img_skelenton_re=flux_img_re>flux_threshold
        img_skelenton_full=img_skelenton_re+img_skelenton
        return(flux_img+flux_img_re,dist_full,img_skelenton_full)

