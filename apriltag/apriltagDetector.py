import sys
sys.path.append('./build')
from apriltag import apriltag
import cv2
import numpy as np
import pdb

import sys
import os
import cv2
import numpy as np
from apriltag import apriltag
import pdb
import json
import argparse

# Add the path where apriltag is located
sys.path.append('./build')

# Set up argument parsing
parser = argparse.ArgumentParser(description='Process images for AprilTag detection.')
parser.add_argument('--task', type=str, required=True, help='Specific task name (e.g., fixedNratio035)')
parser.add_argument('--input_folder', type=str, required=True, help='Destination to get input images')
parser.add_argument('--output_folder', type=str, required=True, help='Destination to store result images and jsons')
parser.add_argument('--store_images', action='store_true', help='Flag to store processed images')
parser.add_argument('--store_jsons', action='store_true', help='Flag to store processed jsons')

args = parser.parse_args()

# Use the task argument
specific_task = args.task
image_folder = args.intput_folder + specific_task
output_folder = args.output_folder + specific_task
os.makedirs(output_folder, exist_ok=True)
# Initialize the AprilTag detector
detector = apriltag("tagStandard41h12")
countsforDetections = 0

# Loop over all files in the folder
for filename in os.listdir(image_folder):
    if filename.endswith('.png'):
        # Construct the full image path
        imagepath = os.path.join(image_folder, filename)
        
        # Read the image in grayscale
        image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)

        # Apply histogram equalization to improve contrast
        equalized_image = cv2.equalizeHist(image)

        # Detect AprilTags in the equalized image
        detections = detector.detect(equalized_image)
        # detections = detector.detect(image)

        # Convert grayscale image to BGR for drawing purposes
        gray = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        countsforDetections += len(detections)
        # Prepare to store detection results in a dictionary
        detection_results = {"detections": []}
        
        if args.store_images:   # draw detections on image and store
            # Loop over the detections and draw the bounding box and tag ID
            for detection in detections:
                # Get the corners of the detected tag
                corners = np.rint(detection['lb-rb-rt-lt']).astype(int)
                
                # Draw the bounding box around the tag (connect the corners)
                cv2.polylines(gray, [corners], isClosed=True, color=(0, 255, 0), thickness=2)
                
                # Draw the tag ID near the center of the tag
                tag_id = detection['id']
                center = tuple(detection['center'].astype(int))
                cv2.putText(gray, str(tag_id), center, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Save the result image to the output folder
            output_path = os.path.join(output_folder, 'output_' + filename)
            cv2.imwrite(output_path, gray)

        if args.store_jsons:
            for detection in detections:        
                # Append detection information to the dictionary
                center = [x.item() for x in np.rint(detection['center']).astype(int)]
                # center = np.rint(detection['center']).astype(int)
                detection_info = {
                    "id": detection['id'],
                    "center": center,
                    "corners": np.rint(detection['lb-rb-rt-lt']).astype(int).tolist()  # Convert numpy array to list for JSON serialization
                }
                detection_results["detections"].append(detection_info)
            results_filename = os.path.splitext(filename)[0] + '_detections.json'
            json_folder = os.path.join(output_folder,'results_json')
            os.makedirs(json_folder, exist_ok=True)
            results_path = os.path.join(json_folder, results_filename)
            with open(results_path, 'w') as f:
                json.dump(detection_results, f, indent=4)  # Save as formatted JSON
print("counts: ", countsforDetections)
print("Processing completed.")

