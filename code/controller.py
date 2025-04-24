# controller.py

import os
from main_window import MainWindow
from model.scanfile_handler import find_plate_files
from model.converter import generate_mov_thumbnail, convert_exr_to_jpg_with_ffmpeg,  convert_to_mp4, convert_to_webm, generate_montage_multi, find_thumbnail_from_montage,  list_excel_versions
from model.excel_manager import save_to_excel, load_excel_data
from model.scan_structure import create_plate_structure
from model.shotgrid_api import connect_to_shotgrid, find_shot, create_version, create_shot, list_projects
import shutil
from PySide6.QtWidgets import QInputDialog

class Controller:
    def __init__(self):
        self.main_window = MainWindow()
        self.folder_path = ""  # 선택된 경로 저장
        self.thumb_cache_dir = "/home/rapa/show"  # 썸네일 저장 위치 위치는 나중에 바꿔주기
    
        self.setup_connections()

    def show_main_window(self):
        self.load_shotgrid_projects()
        self.main_window.show()


    #버튼 연결
    def setup_connections(self):
        self.main_window.select_button.clicked.connect(self.on_select_folder)
        self.main_window.load_button.clicked.connect(self.on_load_files)
        self.main_window.save_button.clicked.connect(self.on_save_excel)
        self.main_window.collect_button.clicked.connect(self.on_collect)
        self.main_window.sg_upload_button.clicked.connect(self.on_register_all_to_shotgrid)
        self.main_window.register_excel_button.clicked.connect(self.on_register_from_selected_excel)

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
            # test3 mov 썸네일 생성
            if item["type"] == "mov":
                thumb_path = generate_mov_thumbnail(item["first_frame_path"], self.thumb_cache_dir)
            else:
                thumb_path = item["first_frame_path"]  # exr/jpg는 첫 프레임 사용

            table_row_data = {
                "thumbnail": thumb_path or "",
                "roll": item["basename"],
                "shot_name": "샷명_자동생성예정",  # 나중에 자동 태깅 가능
                "version": "v001",                # 기본 버전
                "type": item["type"],
                "path": item["seq_dir"],
            }
            pass

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


    # 파일선택 UI
    def on_select_excel_version(self):
        excel_dir = "/home/rapa/show/serin_converter"
        excel_files = list_excel_versions(excel_dir)

        if not excel_files:
            print("❌ 저장된 엑셀 파일이 없습니다.")
            return None

        #  사용자에게 파일 선택 받기
        file_name, ok = QInputDialog.getItem(
            self.main_window,
            "엑셀 버전 선택",
            "샷그리드에 업로드할 엑셀 파일을 선택하세요:",
            excel_files,
            editable=False
        )

        if ok and file_name:
            selected_path = os.path.join(excel_dir, file_name)
            print(f" 선택된파일: {selected_path}")
            return selected_path
        else:
            print("⚠️ 선택 취소됨")
            return None

    # 엑셀 저장 함수 (버전 자동 증가)
    def on_save_excel(self):
        from model.excel_manager import save_to_excel, get_next_versioned_filename

        if self.main_window.table.rowCount() == 0:
            print("⚠️ 테이블에 데이터가 없습니다.")
            return

        # 저장 기본 경로 + 자동 버전명 생성
        base_path = "/home/rapa/show/serin_converter/scanlist.xlsx"
        save_path = get_next_versioned_filename(base_path)

        # 테이블 위젯 기준으로 바로 저장
        save_to_excel(self.main_window.table, save_path)

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
                base_dir = "/home/rapa/show" , # 인자값 이슈로 수정
                shot_name=shot,
                plate_type=plate_type,
                version=version
            )

            # 1. 원본 복사
            for file in os.listdir(src_path):
                if file.lower().endswith((".exr", ".mov", ".mp4")):
                    shutil.copy2(os.path.join(src_path, file), structure["org"])

            # 2. 썸네일 복사 (jpg)
            if thumb_path and os.path.exists(thumb_path):
                shutil.copy2(thumb_path, os.path.join(structure["jpg"], os.path.basename(thumb_path)))

            # 3. 변환 대상 MOV 찾기
            input_video = None
    

            # 1. MOV/MP4가 있으면 우선
            for file in os.listdir(structure["org"]):
                if file.lower().endswith((".mov", ".mp4")):
                    input_video = os.path.join(structure["org"], file)
                    break

            # 2. 없으면 EXR 첫 프레임을 사용 (단일 프레임 기준)
            if not input_video:
                for file in sorted(os.listdir(structure["org"])):
                    if file.lower().endswith(".exr"):
                        input_video = os.path.join(structure["org"], file)
                        break

            # 3. 이제 변환 시작
            if input_video:
                print(f" 변환 대상 파일: {input_video}")
                
                mp4_path = os.path.join(structure["mp4"], f"{shot}_plate_{version}.mp4")
                webm_path = os.path.join(structure["webm"], f"{shot}_plate_{version}.webm")
                montage_path = os.path.join(structure["montage"], f"{shot}_plate_{version}.jpg")

                mp4_ok = convert_to_mp4(input_video, mp4_path)
                webm_ok = convert_to_webm(input_video, webm_path)
                # montage_ok = generate_montage(input_video, montage_path)
                montage_ok = generate_montage_multi(
                    input_video,
                    output_dir=structure["montage"],
                    basename=shot,
                    interval=5,
                    max_frames=10
                )

                print(f"  MP4     : {'✅' if mp4_ok else '❌'} → {mp4_path}")
                print(f"  WebM    : {'✅' if webm_ok else '❌'} → {webm_path}")
                print(f"  Montage : {'✅' if montage_ok else '❌'} → {montage_path}")
            else:
                print(f" {shot} → 변환할 MOV/MP4/EXR 파일이 org 폴더에 없습니다.")

    # # 샷그리드 test 위한 원본 (썸넬 경로 재설정)
    # def on_register_all_to_shotgrid(self):
    #     sg = connect_to_shotgrid()
    #     project_name = "serin_converter"  # 너의 ShotGrid 프로젝트명
      
    
    #     for row in range(self.main_window.table.rowCount()):
    #         shot_name = self.main_window.table.item(row, 3).text()
    #         version = self.main_window.table.item(row, 4).text()
    #         path = self.main_window.table.item(row, 6).text()

    #         # 파일 경로 구성
    #         mp4_path = os.path.join(path, "mp4", version, f"{shot_name}_plate_{version}.mp4")
    #         thumb_path = os.path.join(path, "montage", version, f"{shot_name}_montage_0001.jpg")
    #         montage_dir = os.path.join(path, "montage", version)
    #         thumbnail_path = find_thumbnail_from_montage(montage_dir)
    #         # 샷 찾기
    #         project, shot = find_shot(sg, project_name, shot_name)
    #         if not (project and shot):
    #             print(f"🔎 샷 '{shot_name}'가 존재하지 않아 자동 생성합니다.")
    #             shot = create_shot(sg, project, shot_name, thumb_path)
    #             continue

    #         # Version 등록
    #         print(f"⬆️ 등록 중: {shot_name} / {version}")

    #         create_version(sg, project, shot, version, mp4_path, thumbnail_path)


    # 샷그리드
    def on_register_all_to_shotgrid(self):
        sg = connect_to_shotgrid()
        project_name = "serin_converter"  # 너의 ShotGrid 프로젝트명
      
    
        for row in range(self.main_window.table.rowCount()):
            shot_name = self.main_window.table.item(row, 3).text()
            version = self.main_window.table.item(row, 4).text()
            plate_type = self.main_window.table.item(row, 5).text()
            path = self.main_window.table.item(row, 6).text()

            # 변환된 경로로 재구성
            base_product_root = "/home/rapa/show/serin_converter/product"
            plate_base_path = os.path.join(base_product_root, shot_name, "plate", plate_type, version)

            #  montage 디렉토리 경로
            montage_dir = os.path.join(plate_base_path, "montage")
            thumbnail_path = find_thumbnail_from_montage(montage_dir)

            # 파일 경로 구성
            mp4_path = os.path.join(path, "mp4", version, f"{shot_name}_plate_{version}.mp4")
            thumb_path = os.path.join(path, "montage", version, f"{shot_name}_montage_0001.jpg")
            # 샷 찾기
            project, shot = find_shot(sg, project_name, shot_name)
            if not (project and shot):
                print(f"🔎 샷 '{shot_name}'가 존재하지 않아 자동 생성합니다.")
                shot = create_shot(sg, project, shot_name, thumb_path)
                continue

            # Version 등록
            print(f"⬆️ 등록 중: {shot_name} / {version}")

            create_version(sg, project, shot, version, mp4_path, thumbnail_path)

    def on_register_from_selected_excel(self):

        selected_excel = self.on_select_excel_version()
        if not selected_excel:
            return

        # 프로젝트 선택
        selected_project = self.select_project()
        if not selected_project:
            return

        # 여기에 엑셀 읽고 ShotGrid 등록하는 루프 붙이기
        data_list = load_excel_data(selected_excel)
        sg = connect_to_shotgrid()

        for data in data_list:
            shot_name = data["shot_name"]
            version = data["version"]
            path = data["path"]
            type_ = data["type"]
            mp4_path = os.path.join(path, f"{shot_name}_plate_{version}.mp4")
            montage_dir = os.path.join(path, "montage")
            thumbnail_path = find_thumbnail_from_montage(montage_dir)

            project, shot = find_shot(sg, selected_project["name"], shot_name)
            if not shot:
                shot = create_shot(sg, selected_project, shot_name, thumbnail_path)

            create_version(sg, selected_project, shot, version, mp4_path, thumbnail_path)


    #UI 내 프로젝트 선택함수

    def select_project(self):
        sg = connect_to_shotgrid()
        projects = list_projects(sg)
        project_names = [p["name"] for p in projects]

        project_name, ok = QInputDialog.getItem(
            self.main_window,
            "프로젝트 선택",
            "ShotGrid 프로젝트를 선택하세요:",
            project_names,
            editable=False
        )

        if ok and project_name:
            selected = next(p for p in projects if p["name"] == project_name)
            # 라벨에 표시
            self.main_window.project_label.setText(f"🔘 선택된 프로젝트: {project_name}")
            return selected
        else:
            self.main_window.project_label.setText(f"🛑 선택된 프로젝트: 없음")
            return None
        

    # 프로젝트에 불러와 콤보박스 세팅
    def load_shotgrid_projects(self):
        sg = connect_to_shotgrid()
        self.projects = list_projects(sg)

        self.main_window.project_combo.clear()
        for project in self.projects:
            self.main_window.project_combo.addItem(project["name"])

    

    # 선택된 프로젝트 가져오는 함수
    def get_selected_project(self):
        name = self.main_window.project_combo.currentText()
        selected = next((p for p in self.projects if p["name"] == name), None)
        return selected
    
    # 업로드 시 선택된 프로젝트 사용
    def on_register_from_selected_excel(self):
        selected_excel = self.on_select_excel_version()
        if not selected_excel:
            return

        selected_project = self.get_selected_project()
        if not selected_project:
            print("❌ 프로젝트가 선택되지 않았습니다.")
            return