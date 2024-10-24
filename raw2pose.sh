#!/bin/bash

# Ensure a raw file is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: ./raw2pose.sh <raw_file>"
    exit 1
fi

# Step 1: Convert raw file to H5 format
RAW_FILE="$1"
H5_FILE="${RAW_FILE%.*}.h5"  # Remove the .raw extension and replace it with .h5

echo "Converting raw file to H5 format..."
python3 /event_raw2pose/e2calib/python/convert_raw_to_h5.py "$RAW_FILE" -o "$H5_FILE"

# Check if the H5 file was created
if [ ! -f "$H5_FILE" ]; then
    echo "Error: H5 file not created."
    exit 1
fi

# Step 2: Convert the H5 file to a TXT file
TXT_FILE="${H5_FILE%.*}.txt"  # Replace .h5 with .txt

echo "Converting H5 file to TXT format..."
python3 /event_raw2pose/convert_h5_to_txt.py --input_h5_file "$H5_FILE" --output_file "$TXT_FILE"

# Check if the TXT file was created
if [ ! -f "$TXT_FILE" ]; then
    echo "Error: TXT file not created."
    exit 1
fi

# Step 3: Run reconstruction network to get multiple PNG files
RECONSTRUCTION_OUTPUT_DIR="output_folder/reconstruction"
mkdir -p "$RECONSTRUCTION_OUTPUT_DIR"  # Ensure the output directory exists

echo "Running reconstruction network to generate PNG files..."
python3 /event_raw2pose/rpg_e2vid/run_reconstruction.py -c /event_raw2pose/rpg_e2vid/pretrained/E2VID_lightweight.pth.tar -i "$TXT_FILE" --auto_hdr --show_events -T 33.33 --output_folder "$RECONSTRUCTION_OUTPUT_DIR"

# Check if PNG files were created
if [ ! "$(ls -A $RECONSTRUCTION_OUTPUT_DIR/*.png)" ]; then
    echo "Error: No PNG files generated."
    exit 1
fi

# Step 4: Run AprilTag detection to generate JSON files from PNG files
APRILTAG_OUTPUT_DIR="destination_for_results"
mkdir -p "$APRILTAG_OUTPUT_DIR"

echo "Running AprilTag detection on all reconstructed images..."
python3 /event_raw2pose/apriltag/apriltagDetector.py --input_folder "$RECONSTRUCTION_OUTPUT_DIR" --output_folder "$APRILTAG_OUTPUT_DIR" --store_images --store_jsons

# Check if JSON files were created
if [ ! "$(ls -A $APRILTAG_OUTPUT_DIR/*.json)" ]; then
    echo "Error: No JSON files generated."
    exit 1
fi

# Step 5: Run PnP to calculate camera poses
echo "Running PnP on JSON files to calculate camera poses..."
for json_file in "$APRILTAG_OUTPUT_DIR"/*.json; do
    python3 /event_raw2pose/run_pnp.py --input "$json_file"
done

echo "All steps completed successfully!"
