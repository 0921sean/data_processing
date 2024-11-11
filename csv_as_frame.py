import os
import numpy as np
import pandas as pd

# Define the folder containing the npy files
folder_path = 'D:\Desktop\motion_data_internship\CMU_metric_npy'  # 원하는 폴더 경로로 변경하세요
folder_path_2 = 'D:\Desktop\motion_data_internship\processed_csv'
# Define the new header and the columns to be retained
new_header = [
    'Frame', 'Center of Mass distance', 'Symmetry', 'Grounding', 'Arm fold', 'Leg fold', 
    'Kinetic Energy', 'Potential energy', 'Bone length coherence', 'Torque', 'Center velocity'
]

# Column indices that correspond to these features
selected_columns = [
    0,  # Placeholder for Frame (to be generated)
    0,  # Center of Mass distance
    1,  # Symmetry
    2,  # Grounding
    3,  # Arm fold
    4,  # Leg fold
    5,  # Kinetic Energy
    6,  # Potential energy
    7,  # Bone length coherence
    8,  # Torque
    9,  # Center velocity
]

# List all .npy files in the directory
npy_files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]
i = 0
# Process each .npy file
for npy_file in npy_files:
    # Load the .npy file
    i += 1
    file_path = os.path.join(folder_path, npy_file)
    data = np.load(file_path)
    
    # Select the relevant columns
    selected_data = data[:, selected_columns[1:]]  # Skip Frame for now, it's generated

    # Create a DataFrame and add a Frame column
    df = pd.DataFrame(selected_data, columns=new_header[1:])
    df.insert(0, 'Frame', range(1, len(df) + 1))
    npy_file = npy_file.replace(".npy", "")
    # Save the DataFrame to a CSV file with the same name as the .npy file
    csv_file_path = os.path.join(folder_path_2, f"{npy_file}.csv")
    df.to_csv(csv_file_path, index=False)
    