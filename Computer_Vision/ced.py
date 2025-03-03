import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

# Create a 5x5 Gaussian kernel with σ=1.0
def create_gaussian_kernel(size=5, sigma=1.0):
    kernel = np.zeros((size, size))
    center = size // 2
    
    for i in range(size):
        for j in range(size):
            x = i - center
            y = j - center
            kernel[i, j] = (1/(2*np.pi*sigma**2)) * np.exp(-(x**2 + y**2)/(2*sigma**2))
    
    # Normalize the kernel
    kernel = kernel / kernel.sum()
    return kernel

# Custom convolution function
def convolve2d(image, kernel):
    kernel_height, kernel_width = kernel.shape
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2
    
    padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
    output = np.zeros_like(image, dtype=np.float64)
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            output[i, j] = np.sum(padded_image[i:i+kernel_height, j:j+kernel_width] * kernel)
    
    return output

# Read and convert image to grayscale
image = cv2.imread('./Lab 1.jpg')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

plt.figure(figsize=(12, 8))
plt.subplot(231), plt.imshow(gray_image, cmap='gray'), plt.title('Original Image')

# Create and apply Gaussian kernel
gaussian_kernel = create_gaussian_kernel(5, 1.0)
blurred_image = convolve2d(gray_image, gaussian_kernel)

plt.subplot(232), plt.imshow(blurred_image, cmap='gray'), plt.title('Gaussian Smoothed')

# Define Sobel kernels
sobel_x_kernel = np.array([[-1, 0, 1],
                          [-2, 0, 2],
                          [-1, 0, 1]])

sobel_y_kernel = np.array([[-1, -2, -1],
                          [0, 0, 0],
                          [1, 2, 1]])

# Apply Sobel operators using custom convolution
Gx = convolve2d(blurred_image, sobel_x_kernel)
Gy = convolve2d(blurred_image, sobel_y_kernel)

# Calculate gradient magnitude and direction
G = np.sqrt(Gx**2 + Gy**2)
theta = np.arctan2(Gy, Gx)

plt.subplot(233), plt.imshow(G, cmap='gray'), plt.title('Gradient Magnitude')

# Convert angles to degrees and adjust to 4 directions
angle_degrees = np.rad2deg(theta) % 180
angle_degrees = np.round(angle_degrees / 45) * 45

# Non-Maximum Suppression
M, N = G.shape
Z = np.zeros((M, N), dtype=np.float32)

for i in range(1, M-1):
    for j in range(1, N-1):
        try:
            q = 255
            r = 255
            
            # Angle 0
            if (0 <= angle_degrees[i, j] < 22.5) or (157.5 <= angle_degrees[i, j] <= 180):
                q = G[i, j+1]
                r = G[i, j-1]
            # Angle 45
            elif 22.5 <= angle_degrees[i, j] < 67.5:
                q = G[i+1, j-1]
                r = G[i-1, j+1]
            # Angle 90
            elif 67.5 <= angle_degrees[i, j] < 112.5:
                q = G[i+1, j]
                r = G[i-1, j]
            # Angle 135
            elif 112.5 <= angle_degrees[i, j] < 157.5:
                q = G[i-1, j-1]
                r = G[i+1, j+1]

            if (G[i, j] >= q) and (G[i, j] >= r):
                Z[i, j] = G[i, j]
            else:
                Z[i, j] = 0

        except IndexError as e:
            pass

plt.subplot(234), plt.imshow(Z, cmap='gray'), plt.title('Non-Max Suppression')

# Double Thresholding
high_threshold = np.percentile(Z, 90)
low_threshold = high_threshold * 0.3

strong_edges = (Z > high_threshold)
weak_edges = (Z >= low_threshold) & (Z <= high_threshold)
non_edges = (Z < low_threshold)

edges = np.zeros_like(Z, dtype=np.uint8)
edges[strong_edges] = 255
edges[weak_edges] = 128

plt.subplot(235), plt.imshow(edges, cmap='gray'), plt.title('Double Thresholding')

# Hysteresis
final_edges = np.copy(edges)
M, N = edges.shape

for i in range(1, M-1):
    for j in range(1, N-1):
        if edges[i, j] == 128:
            if 255 in [edges[i+1, j-1], edges[i+1, j], edges[i+1, j+1],
                      edges[i, j-1], edges[i, j+1],
                      edges[i-1, j-1], edges[i-1, j], edges[i-1, j+1]]:
                final_edges[i, j] = 255
            else:
                final_edges[i, j] = 0

plt.subplot(236), plt.imshow(final_edges, cmap='gray'), plt.title('After Hysteresis')
plt.tight_layout()
plt.show()
