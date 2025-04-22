# controller.py

import os
from main_window import MainWindow
from model.scanfile_handler import find_plate_files
from model.converter import generate_mov_thumbnail, convert_exr_to_jpg_with_ffmpeg
from model.excel_manager import save_to_csv


class Controller:
    def __init__(self):
        self.main_window = MainWindow()
        self.folder_path = ""  # 선택된 경로 저장
        self.thumb_cache_dir = "/home/rapa/westworld_serin/converter"  # 썸네일 저장 위치 위치는 나중에 바꿔주기
    
        self.setup_connections()

    def show_main_window(self):
        self.main_window.show()

    def setup_connections(self):
        self.main_window.select_button.clicked.connect(self.on_select_folder)
        self.main_window.load_button.clicked.connect(self.on_load_files)
        self.main_window.save_button.clicked.connect(self.on_save_excel)

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
                "shot_name": "샷명_자동생성예정",
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
