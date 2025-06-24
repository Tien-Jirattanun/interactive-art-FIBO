import cv2
import numpy as np
import glob

CHECKERBOARD = (9, 6)  # inner corners (not squares)
square_size = 0.020  # meters

objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []  # 3D points
imgpoints = []  # 2D points

images = glob.glob('calib_images/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

# Calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera Matrix:\n", mtx)
print("Distortion Coefficients:\n", dist)

np.savez("calibration_data.npz", camera_matrix=mtx, dist_coeffs=dist)
