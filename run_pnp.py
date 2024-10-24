import cv2
import numpy as np
import json
import sys
from pathlib import Path

# Check if a JSON input file is provided
if len(sys.argv) < 2:
    print("Usage: python3 run_pnp.py --input <json_file>")
    exit(1)

# Parse the JSON input file from the command line argument
json_file = sys.argv[2]
json_path = Path(json_file)

# Ensure the JSON file exists
if not json_path.exists():
    print(f"Error: JSON file {json_file} not found.")
    exit(1)

# Load the JSON data
with open(json_path, 'r') as f:
    data = json.load(f)

# Function to get AprilTag corners for a specific tag id
def get_april_tag_corners_np(detections, tag_ids):
    """
    Try to find the corners for any of the tag IDs in the list.
    Returns the corners as a NumPy array or None if no tag is found.
    """
    for tag_id in tag_ids:
        for detection in detections:
            if detection['id'] == tag_id:
                # Convert corners to a NumPy array of type float32
                print(f"AprilTag with ID {tag_id} found.")
                return np.array(detection['corners'], dtype=np.float32)
    return None

# AprilTag IDs to look for (2 and 3)
tag_ids = [2, 3]

# Extract image points (2D corners in the image)
img_points = get_april_tag_corners_np(data['detections'], tag_ids)

if img_points is None:
    print(f"No AprilTag with ID 2 or 3 found in {json_file}.")
    exit(1)

# Ensure img_points is the correct shape (4x2)
if img_points.shape != (4, 2):
    print(f"Error: Expected img_points to have shape (4, 2), but got {img_points.shape}.")
    exit(1)

# Define 3D object points (corners of the AprilTag in the real world)
tag_size = 0.03  # Size of the tag in meters (30 mm)
half_size = tag_size / 2
obj_points = np.array([
    [-half_size, -half_size, 0],
    [half_size, -half_size, 0],
    [half_size, half_size, 0],
    [-half_size, half_size, 0]
], dtype=np.float32)

# Camera intrinsic parameters
K = np.array([[1697.5032983141937, 0, 645.1074784908191],
              [0, 1695.7094152984062, 363.99501423203714],
              [0,  0,  1]], dtype=np.float32)

# Distortion coefficients
dist_coeffs = np.array([-0.10042486096826046, 0.3633220517960035,
                        -0.00021321537553025432, 0.0010524550740930226], dtype=np.float32)

# Perform solvePnP to estimate the pose of the camera
success, rvec, tvec = cv2.solvePnP(obj_points, img_points, K, dist_coeffs)

if success:
    # Print the rotation vector (rvec) and translation vector (tvec)
    print(f"Camera pose for {json_file}:")
    print("Rotation Vector (rvec):\n", rvec)
    print("Translation Vector (tvec):\n", tvec)

    # Convert the rotation vector to a rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    print("Rotation Matrix:\n", rotation_matrix)
else:
    print(f"solvePnP failed to estimate the camera pose for {json_file}.")
