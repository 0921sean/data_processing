# CMU to metric

import torch
from all_metric import *

def extractingall(motion):
    f1 = get_COM_to_plane(motion)
    f2 = symmetry(motion)
    f3 = grounding(motion)
    f4 = get_arm_folding_level(motion)
    f5 = get_leg_folding_level(motion)
    f6 = get_kinetic_energy(motion) #-1
    f7 = get_potential_Energy(motion) #-1
    f8 = relative_bonelength(motion)
    f9 = get_torque(motion) #-2
    f10 = get_center_velocity(motion) #-1

    f6 = np.insert(f6, 0, f6[0], axis=0)
    f7 = np.insert(f7, 0, f7[0], axis=0)
    f9 = np.insert(f9, 0, f9[0], axis=0)
    f9 = np.insert(f9, -1, f9[-1], axis=0)
    f10 = np.insert(f10, 0, f10[0], axis=0)

    f1 = np.reshape(f1,(-1,1))
    f2 = np.reshape(f2,(-1,1))
    f3 = np.reshape(f3,(-1,1))
    f4 = np.reshape(f4,(-1,1))
    f5 = np.reshape(f5,(-1,1))
    f6 = np.reshape(f6,(-1,1))
    f7 = np.reshape(f7,(-1,1))
    f8 = np.reshape(f8,(-1,1))
    f9 = np.reshape(f9,(-1,1))
    f10 = np.reshape(f10,(-1,1))


    concate_feature = np.concatenate((f1, f2, f3, f4, f5,
                                      f6, f7, f8, f9, f10,), axis=1) # (frame, 10)

    #concate_feature = torch.tensor(concate_feature)

    return concate_feature

def extracting18(motion):
    f1 = get_COM_to_plane(motion)
    f2 = symmetry(motion)
    f3 = grounding(motion)
    f4 = get_arm_folding_level(motion)
    f5 = get_leg_folding_level(motion)
    f6 = get_kinetic_energy(motion)  # -1
    f7 = get_potential_Energy(motion)  # -1
    f8 = relative_bonelength(motion)
    f9 = get_torque(motion)  # -2
    f10 = get_center_velocity(motion)  # -1
    f11 = get_edge_angular_velocity(motion)  # -1
    f12, f13 = get_edge_angular_velocity_arm(motion)  # -1
    f14, f15 = get_edge_angular_velocity_leg(motion)  # -1
    f16 = part_attention_score(motion)  # -1
    f17 = efficiency(motion)  # -5
    f18 = get_area_score(motion)  # -1

    f6 = np.insert(f6, 0, f6[0], axis=0)
    f7 = np.insert(f7, 0, f7[0], axis=0)
    f9 = np.insert(f9, 0, f9[0], axis=0)
    f9 = np.insert(f9, -1, f9[-1], axis=0)
    f10 = np.insert(f10, 0, f10[0], axis=0)
    f11 = np.insert(f11, 0, f11[0], axis=0)
    f12 = np.insert(f12, 0, f12[0], axis=0)
    f13 = np.insert(f13, 0, f13[0], axis=0)
    f14 = np.insert(f14, 0, f14[0], axis=0)
    f15 = np.insert(f15, 0, f15[0], axis=0)
    f16 = np.insert(f16, 0, f16[0], axis=0)
    f17 = np.insert(f17, [0,1,2], f17[0], axis=0)
    f17 = np.insert(f17, [-1,-2], f17[0], axis=0)
    f18 = np.insert(f18, 0, f18[0], axis=0)

    f1 = np.reshape(f1,(-1,1))
    f2 = np.reshape(f2,(-1,1))
    f3 = np.reshape(f3,(-1,1))
    f4 = np.reshape(f4,(-1,1))
    f5 = np.reshape(f5,(-1,1))
    f6 = np.reshape(f6,(-1,1))
    f7 = np.reshape(f7,(-1,1))
    f8 = np.reshape(f8,(-1,1))
    f9 = np.reshape(f9,(-1,1))
    f10 = np.reshape(f10,(-1,1))
    f11 = np.reshape(f11,(-1,1))
    f12 = np.reshape(f12, (-1, 1))
    f13 = np.reshape(f13, (-1, 1))
    f14 = np.reshape(f14, (-1, 1))
    f15 = np.reshape(f15, (-1, 1))
    f16 = np.reshape(f16,(-1,1))
    f17 = np.reshape(f17,(-1,1))
    f18 = np.reshape(f18,(-1, 1))


    concate_feature = np.concatenate((f1, f2, f3, f4, f5,
                                      f6, f7, f8, f9, f10,
                                      f11,f12,f13,f14,f15,
                                      f16,f17,f18), axis=1) # (frame, 24)

    concate_feature = torch.tensor(concate_feature)

    return concate_feature

def normalize_columns(data):
    """
    열 방향으로 NumPy 배열을 0에서 1 사이로 정규화하는 함수
    
    Parameters:
    data (np.ndarray): 정규화할 NumPy 배열
    
    Returns:
    np.ndarray: 열 방향으로 정규화된 NumPy 배열
    """
    # 각 열의 최소값과 최대값 계산
    col_min = data.min(axis=0)  # 열별 최소값
    col_max = data.max(axis=0)  # 열별 최대값
    
    # 최소-최대 정규화 수행, 최대값과 최소값이 같은 경우 0으로 설정
    normalized_data = (data - col_min) / (col_max - col_min + 1e-8)
    
    return normalized_data


if __name__ == "__main__":
    import os
    import numpy as np
    import pandas as pd
    folder_path = "D:\\Desktop\\motion_data_internship\\CMU_csv_jointpos"
    csv_files = [f for f in os.listdir(folder_path)]
    for csv_file in csv_files:
        motion_path = os.path.join(folder_path, csv_file)
        motion_data = np.loadtxt(motion_path, delimiter=",")
        motion_data = np.reshape(motion_data, (-1, 15, 3))
        motion_data = motion_data[1:]

        from utils import *

        #norm_motion_data = normalize_using_headneck(motion_data)
        a = extractingall(motion_data)
        normalized_data = normalize_columns(a)
        csv_file = csv_file.replace(".csv", "")
        csv_file = csv_file.replace("poses", "")
        
        np.save(f"D:\\Desktop\\motion_data_internship\\CMU_metric_npy\\{csv_file}.npy", normalized_data)

        
