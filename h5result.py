import numpy as np
import h5py
import pdb

# Open the HDF5 file
with h5py.File('april_tags_2.h5', 'r') as file:
    # List all groups (keys)
    print("Keys:", list(file.keys()))
    event_xs = np.array(file['x'])
    event_ys = np.array(file['y'])
    event_ts = np.array(file['t'])
    event_ps = np.array(file['p'])
    # Stack arrays column-wise
    data = np.column_stack((event_ts, event_xs, event_ys, event_ps))
# Open the output file in write mode
with open('h5result.txt', 'w') as f:
    # Write the "1280 720" as the first line
    f.write("1280 720\n")
    
    # Save the data using np.savetxt, appending to the same file
    np.savetxt(f, data, fmt='%d')