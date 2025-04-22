# model/scan_structure.py
""" 각 row에 대해 자동으로 다음 작업 수행:

샷 이름 기반 폴더 구조 생성

org/ 폴더로 원본 파일 복사

jpg/, mp4/, webm/, montage/ 폴더로 변환 이미지 생성
"""


import os
import shutil

# def create_plate_structure(base_dir, shot_name, plate_type, version):
#     """
#     샷 이름 기준 plate 폴더 구조 생성
#     """
#     plate_root = os.path.join(base_dir, shot_name, "plate", plate_type, version)
#     subfolders = ["org", "jpg", "mp4", "webm", "montage"]

#     created_paths = {}
#     for sub in subfolders:
#         path = os.path.join(plate_root, sub)
#         os.makedirs(path, exist_ok=True)
#         created_paths[sub] = path

#     return created_paths  # dict

# model/scan_structure.py

import os

def create_plate_structure(shot_name, plate_type, version):
    """
    지정된 경로에 /product/{shot_name}/plate/{type}/{version}/ 구조 생성
    """
    base_root = "/home/rapa/westworld_serin/converter/product"  #  고정 base path
    plate_root = os.path.join(base_root, shot_name, "plate", plate_type, version)

    subfolders = ["org", "jpg", "mp4", "webm", "montage"]
    created_paths = {}

    for sub in subfolders:
        path = os.path.join(plate_root, sub)
        os.makedirs(path, exist_ok=True)
        created_paths[sub] = path

    return created_paths
