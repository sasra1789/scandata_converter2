# controller.py

import os
from main_window import MainWindow
from model.scanfile_handler import find_plate_files
from model.converter import generate_mov_thumbnail, convert_exr_to_jpg_with_ffmpeg,  convert_to_mp4, convert_to_webm, generate_montage
from model.excel_manager import save_to_csv
from model.scan_structure import create_plate_structure
import shutil


class Controller:
    def __init__(self):
        self.main_window = MainWindow()
        self.folder_path = ""  # 선택된 경로 저장
        self.thumb_cache_dir = "/home/rapa/westworld_serin/converter"  # 썸네일 저장 위치 위치는 나중에 바꿔주기
    
        self.setup_connections()

    def show_main_window(self):
        self.main_window.show()


    #버튼 연결
    def setup_connections(self):
        self.main_window.select_button.clicked.connect(self.on_select_folder)
        self.main_window.load_button.clicked.connect(self.on_load_files)
        self.main_window.save_button.clicked.connect(self.on_save_excel)
        self.main_window.collect_button.clicked.connect(self.on_collect)

    # 디렉토리 선택하고 path 라벨에 표시
    def on_select_folder(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self.main_window, "스캔 폴더 선택")
        if folder:
            self.folder_path = folder
            self.main_window.set_path(folder)

    # scanfile_handler 로 .exr, .mov 파일 읽고, 썸네일 생성 
    def on_load_files(self):
        if not self.folder_path:
            print(" 폴더가 선택되지 않았습니다.")
            return

        file_items = find_plate_files(self.folder_path)

        for item in file_items:
            # test 2
            if item["type"] == "sequence":
                thumb_jpg = os.path.join(
                    self.thumb_cache_dir,
                    os.path.splitext(os.path.basename(item["first_frame_path"]))[0] + "_thumb.jpg"
                )
                if not os.path.exists(thumb_jpg):
                    convert_exr_to_jpg_with_ffmpeg(item["first_frame_path"], thumb_jpg)
                thumb_path = thumb_jpg
            else:
                thumb_path = generate_mov_thumbnail(item["first_frame_path"], self.thumb_cache_dir)

            table_row_data = {
                "thumbnail": thumb_path or "",
                "roll": item["basename"],
                "shot_name": "S샷명을_SH입력해주세요",
                "version": "v001",
                "type": item["type"],
                "path": item["seq_dir"],
            }
            self.main_window.add_table_row(table_row_data)


    # 엑셀추가
    def on_save_excel(self):
        from PySide6.QtWidgets import QFileDialog

        if self.main_window.table.rowCount() == 0:
            print(" 테이블에 데이터가 없습니다.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "CSV 저장 위치",
            "scanlist_01.csv",
            "CSV Files (*.csv)"
        )

        if save_path:
            data_list = []

            for row in range(self.main_window.table.rowCount()):
                thumb_widget = self.main_window.table.cellWidget(row, 1)
                thumbnail = thumb_widget.toolTip() if thumb_widget else ""
                roll = self.main_window.table.item(row, 2).text()
                shot = self.main_window.table.item(row, 3).text()
                version = self.main_window.table.item(row, 4).text()
                type_ = self.main_window.table.item(row, 5).text()
                path = self.main_window.table.item(row, 6).text()

                data_list.append({ 
                    "thumbnail": thumbnail ,
                    "roll": roll,
                    "shot_name": shot,
                    "version": version,
                    "type": type_,
                    "path": path,
                })

            save_to_csv(data_list, save_path)

    def on_collect(self):
        if not self.folder_path:
            print(" 경로가 지정되지 않았습니다.")
            return

        for row in range(self.main_window.table.rowCount()):
            shot = self.main_window.table.item(row, 3).text()           # shot_name
            plate_type = self.main_window.table.item(row, 5).text()     # type
            version = self.main_window.table.item(row, 4).text()        # version
            src_path = self.main_window.table.item(row, 6).text()       # 원본 위치

            # 썸네일 위젯에서 jpg 경로 추출 (toolTip에 저장해두었다면)
            thumb_label = self.main_window.table.cellWidget(row, 1)
            thumb_path = thumb_label.toolTip() if thumb_label else None
            

            structure = create_plate_structure(
                shot_name=shot,
                plate_type=plate_type,
                version=version
            )
            # #원본
            # # org에 파일 복사
            # for file in os.listdir(src_path):
            #     if file.endswith((".exr", ".mov")):
            #         shutil.copy2(os.path.join(src_path, file), structure["org"])

            # # jpg 저장
            # if thumb_path and os.path.exists(thumb_path):
            #     shutil.copy2(thumb_path, os.path.join(structure["jpg"], os.path.basename(thumb_path)))

            # print(f" 폴더 생성 및 복사 완료: {shot}")

            # 1. 원본 복사
            for file in os.listdir(src_path):
                if file.lower().endswith((".exr", ".mov", ".mp4")):
                    shutil.copy2(os.path.join(src_path, file), structure["org"])

            # 2. 썸네일 복사 (jpg)
            if thumb_path and os.path.exists(thumb_path):
                shutil.copy2(thumb_path, os.path.join(structure["jpg"], os.path.basename(thumb_path)))

            # 3. 변환 대상 MOV 찾기
            input_video = None
            for file in os.listdir(structure["org"]):
                if file.lower().endswith((".mov", ".mp4")):
                    input_video = os.path.join(structure["org"], file)
                    break

            # # org 폴더에서 mov 파일 찾기
            # for file in os.listdir(structure["org"]):
            #     if file.endswith(".mov"):
            #         input_video = os.path.join(structure["org"], file)
            #         break
            

            if input_video:
                mp4_path = os.path.join(structure["mp4"], f"{shot}_plate_{version}.mp4")
                webm_path = os.path.join(structure["webm"], f"{shot}_plate_{version}.webm")
                montage_path = os.path.join(structure["montage"], f"{shot}_plate_{version}.jpg")

                convert_to_mp4(input_video, mp4_path)
                convert_to_webm(input_video, webm_path)
                generate_montage(input_video, montage_path)

                print(f" 변환 완료: {shot}")