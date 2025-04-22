# model/scanfile_handler.py

import os
import pyseq

def find_plate_files(folder_path, extensions=[".exr", ".jpg", ".dpx"], video_exts=[".mov"]):
    """
    주어진 폴더에서 이미지 시퀀스와 MOV 파일 탐지
    :return: 리스트(dict), 썸네일 경로, 경로, 종류(type), 기타 정보 포함
    """
    if not os.path.exists(folder_path):
        return []

    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    print("로드된 항목 수:", len(all_files))  #  확인 포인트
    
    # 1시퀀스 그룹핑 (EXR 등)
    sequences = pyseq.get_sequences(all_files)
    seq_items = []

    for seq in sequences:
        ext = seq.format('%t').lower()
        if ext in extensions:
            seq_info = {
                "type": "sequence",
                "head": seq.head(),
                "tail": seq.tail(),
                "start": seq.start(),
                "end": seq.end(),
                "length": len(seq),
                "first_frame_path": seq[0].path,
                "seq_dir": os.path.dirname(seq[0].path),
                "basename": seq.format('%h%p%t'),
            }
            seq_items.append(seq_info)

    # 2 MOV 파일 찾기
    mov_items = []
    for file in all_files:
        if os.path.isfile(file) and os.path.splitext(file)[1].lower() in video_exts:
            mov_info = {
                "type": "mov",
                "first_frame_path": file,  # 썸네일용
                "basename": os.path.basename(file),
                "seq_dir": os.path.dirname(file),
                "length": 1, # 프레임수 또는 1 
                "start": 0,
                "end": 0,
            }
            mov_items.append(mov_info)

    return seq_items + mov_items
