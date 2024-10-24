# event_raw2pose

## Required Repositories



[High Speed and High Dynamic Range Video with an Event Camera] (https://github.com/uzh-rpg/rpg_e2vid)

[AprilTag 3] (https://github.com/AprilRobotics/apriltag)

## Run the complete raw-to-camera_pose pipeline using one command
```bash
bash raw2pose.sh
```

## Steps
First, convert the RAW file to the h5 file using e2calib.
```bash
python3 convert.py april_tags.raw
```

Once we get the h5 file converted from RAW. We should convert it to TXT so that the input format meet the requirement of E2VID:
```bash
python convert_h5_to_txt.py --input_h5_file your_ht_file --output_file output_file.txt
```


For Image reconstruction from events, we need to prepare the conda environment first:
```bash
conda create -n E2VID
conda activate E2VID
conda install pytorch torchvision cudatoolkit=10.0 -c pytorch
conda install pandas
conda install -c conda-forge opencv
```

In the Conda environment E2VID, type the following command to reconstruct images in specific fps. -T represents the window period in ms.  
```bash
python run_reconstruction.py   -c pretrained/E2VID_lightweight.pth.tar   -i input.txt   --auto_hdr --show_events -T 33.33 --output_folder output_folder/reconstruction
```

For apriltag detection, the apriltage repository need to be complied first. 
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target install
```
Then run apriltagDetector.py in apriltag folder
```bash
python apriltagDetector.py --input_folder reconstructed_images_folder  --output_folder destination_for_results --store_images --store_jsons
```
At last, do PnP to the json files to print out the poses by 
```bash
python3 run_pnp.py
```

