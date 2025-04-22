# model/excel_manager.py

import csv
import os

def save_to_csv(data_list, save_path):
    """
    테이블 데이터를 CSV로 저장
    썸네일은 경로만 텍스트로 저장됨
    """
    headers = ["Thumbnail", "Roll", "Shot Name", "Version", "Type", "Path"]

    with open(save_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in data_list:
            writer.writerow({
                "Thumbnail": item["thumbnail"], 
                "Roll": item["roll"],
                "Shot Name": item["shot_name"],
                "Version": item["version"],
                "Type": item["type"],
                "Path": item["path"],
            })

    print(f" CSV 저장 완료: {save_path}")
