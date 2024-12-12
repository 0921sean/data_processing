# SMPL to CMU
# (n, 15, 3) 차원 npy 파일로 저장

from smplx import SMPL # SMPLX로 해주세요.
import torch
import numpy as np
import os

import pandas as pd

# Define the folder containing the npy files
folder_path = 'D:\\Desktop\\SMPL_python_v.1.0.0\\HumanML3D\\pose_data\\CMU'  # 원하는 폴더 경로로 변경하세요
# List all .npy files in the directory
npy_folders = [f for f in os.listdir(folder_path)]
i = 0

for npy_folder in npy_folders:
    folder_path2 = os.path.join(folder_path, npy_folder)
    npy_files = [f for f in os.listdir(folder_path2) if f.endswith('.npy')]
    for npy_file in npy_files:
        file_path = os.path.join(folder_path2, npy_file)
        data = np.load(file_path)
        data = data[:,:24,:]

        smpl = SMPL(model_path='D:\\Desktop\\SMPL_python_v.1.0.0\\SMPL_MALE.pkl', batch_size=1)
        # SMPL은 GPU를 사용하는 게 아닌 단순 라이브러리입니다. 변환을 위해서 다음과 같이 불러만 오면 됩니다.
        pose_npy = np.reshape(data, (-1, 72))
        pose_th = torch.from_numpy(pose_npy).float()

        transl_th = torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float32)
        # shape 쪽 파라미터입니다. 임의로 0으로 설정

        # By forward pass through SMPL model, obtain joint positions
        output = smpl(global_orient=pose_th[:, :3], body_pose=pose_th[:, 3:], transl=transl_th)
        joints_npy = output.joints.detach().numpy() # Extract joint positions as a NumPy array

        joints_npy = joints_npy[:,:24]  # Select which contain the necessary 15 joints

        # Rearrange the necessary 15 key joints to match the required format for later processing
        reshape = [0, 9, 17, 19, 21, 16, 18, 20, 15, 2, 5, 8, 1, 4, 7]  # Indices of the 15 main joints
        selected_joints = joints_npy[:,reshape,:]  # Select and reorder the 15 main joints
        joints_npy = np.reshape(selected_joints, (-1,45))   # Shape becomes (frame_num, 45)
        
        save_path = os.path.join("D:\Desktop\motion_data_internship\CMU_csv_jointpos", )
        npy_file = npy_file.replace(".npy", "")
        np.savetxt(f"D:\\Desktop\\motion_data_internship\\CMU_csv_jointpos\\{npy_file}.csv", joints_npy, delimiter=",")
