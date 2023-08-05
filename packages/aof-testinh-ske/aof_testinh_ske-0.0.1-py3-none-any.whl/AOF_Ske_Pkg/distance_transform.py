import scipy.ndimage.morphology as morphOps

def get_distance_transform(grayscale_img):
    return morphOps.distance_transform_edt(grayscale_img, return_indices=True)