import numpy as np
import PIL
import matplotlib.pyplot as plt 

def otsu_thresholding(image):
    image = np.array(PIL.Image.open(image))
    intensities = np.unique(image)
    print(intensities)
    plt.imshow(image)
    
    
otsu_thresholding('./Lab 1.jpg')