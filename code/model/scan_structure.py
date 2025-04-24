# model/scan_structure.py
""" 각 row에 대해 자동으로 다음 작업 수행:

샷 이름 기반 폴더 구조 생성

org/ 폴더로 원본 파일 복사

jpg/, mp4/, webm/, montage/ 폴더로 변환 이미지 생성
"""


import os
import shutil

def create_plate_structure(base_dir, shot_name, plate_type, version):
    """
    plate/{type}/{version}/ 안에 필요한 구조 생성
    단, mp4/webm은 별도 폴더 없이 version 폴더 내부에 파일만 저장
    """
    plate_root = os.path.join(base_dir, shot_name, "plate", plate_type, version)
    os.makedirs(plate_root, exist_ok=True)

    subfolders = ["org", "jpg", "montage"]  
    created_paths = {}

    for sub in subfolders:
        path = os.path.join(plate_root, sub)
        os.makedirs(path, exist_ok=True)
        created_paths[sub] = path

    #  mp4/webm은 파일 경로만 미리 정의해 반환
    created_paths["mp4"] = os.path.join(plate_root, f"{shot_name}_plate_{version}.mp4")
    created_paths["webm"] = os.path.join(plate_root, f"{shot_name}_plate_{version}.webm")

    return created_paths