import cv2
import numpy as np
import matplotlib.pyplot as plt

# Define the dictionary we want to use
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# generate markers
marker_id = 0;
marker_size = 200
marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)

# Save the marker image and display it
cv2.imwrite('marker_0.png', marker_image)
plt.imshow(marker_image, cmap='gray', interpolation='nearest')
plt.axis('off')  # Hide axes
plt.title(f'ArUco Marker {marker_id}')
plt.show()
