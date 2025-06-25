import cv2
import cv2.aruco as aruco
import numpy as np
from math import atan2, asin, degrees

# --- Load camera parameters ---
with np.load("calibration_data.npz") as X:
    camera_matrix = X["camera_matrix"]
    dist_coeffs = X["dist_coeffs"]

# --- Parameters ---
marker_length = 0.055  # in meters

# --- Setup video capture ---
cap = cv2.VideoCapture(1)
aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect markers
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    if ids is not None:
        # Estimate pose
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
        for i in range(len(ids)):
            # Draw axis
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.05)

            # Get translation
            position = tvecs[i][0]  # x, y, z in meters

            # Convert rotation vector to rotation matrix
            R, _ = cv2.Rodrigues(rvecs[i])

            # Compute roll, pitch, yaw
            def rotationMatrixToEulerAngles(R):
                sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
                singular = sy < 1e-6

                if not singular:
                    x = atan2(R[2, 1], R[2, 2])
                    y = atan2(-R[2, 0], sy)
                    z = atan2(R[1, 0], R[0, 0])
                else:
                    x = atan2(-R[1, 2], R[1, 1])
                    y = atan2(-R[2, 0], sy)
                    z = 0
                return np.array([degrees(x), degrees(y), degrees(z)])

            rpy = rotationMatrixToEulerAngles(R)

            print(f"ID: {ids[i][0]}")
            print(f"Position (x, y, z) [m]: {position}")
            print(f"Rotation (roll, pitch, yaw) [deg]: {rpy}")

    # Show image
    cv2.imshow("ARUCO Pose", frame)
    if cv2.waitKey(1) == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
