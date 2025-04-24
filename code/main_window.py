# main_window.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QTableWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QTableWidgetItem, QCheckBox, QComboBox
)
from PySide6.QtGui import QPixmap
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScanData IO Manager")
        self.setMinimumSize(1200, 800)

        # ==== 위쪽: 경로 및 버튼 ====
        self.path_label = QLabel(" 경로를 선택하세요")
        self.select_button = QPushButton("Select")
        self.load_button = QPushButton("Load")

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.select_button)
        path_layout.addWidget(self.load_button)

        # ==== 중간: 테이블 ====
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Check", "Thumbnail", "Roll", "Shot Name", "Version", "Type", "Path"
        ])

        # ==== 아래쪽: 액션 버튼 ====
        self.save_button = QPushButton("Save Excel")
        self.collect_button = QPushButton("Collect")
        

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.collect_button)

        #샷그리드 등록버튼
        self.sg_upload_button = QPushButton("Register to ShotGrid")
        bottom_layout.addWidget(self.sg_upload_button)

        # 엑셀 선택하여 샷그리드에 바로 업로드
        self.register_excel_button = QPushButton("엑셀 선택 → ShotGrid 업로드")
        bottom_layout.addWidget(self.register_excel_button)


        # 프로젝트에 바로 뜨도록 하기 
        self.project_label = QLabel("🔘 선택된 프로젝트: 없음")
        bottom_layout.addWidget(self.project_label)


        # 프로젝트 선택 UI
        self.project_combo_label = QLabel("📁 프로젝트 선택:")
        self.project_combo = QComboBox()
        # 초기화 시 기본값
        self.project_combo.addItem("🔄 ShotGrid 프로젝트 불러오는 중...")

        # 위쪽레이아웃에 추가
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.project_combo_label)
        top_layout.addWidget(self.project_combo)

        # ==== 전체 레이아웃 ====
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(path_layout)
        layout.addWidget(self.table)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def set_path(self, path):
        self.path_label.setText(path)

    # def add_table_row(self, data):
    #     """
    #     data = {
    #         'thumbnail': path_to_jpg,
    #         'roll': 'ROLL001',
    #         'shot_name': 'S001_SH0010',
    #         'version': 'v001',
    #         'type': 'org',
    #         'path': '/scan/...'
    #     }
    #     """
    #     row = self.table.rowCount()
    #     self.table.insertRow(row)

    #     # CheckBox
    #     checkbox = QCheckBox()
    #     self.table.setCellWidget(row, 0, checkbox)


    #     # Thumbnail
    #     thumb_label = QLabel()
    #     thumb_label.setFixedSize(100, 60)
    #     thumb_label.setStyleSheet("border: 1px solid #999;")
    #     thumb_label.setScaledContents(True)

    #     if os.path.exists(data['thumbnail']):
    #         pixmap = QPixmap(data['thumbnail'])
    #         if not pixmap.isNull():
    #             thumb_label.setPixmap(pixmap)
    #         else:
    #             print("❌ QPixmap이 null입니다:", data['thumbnail'])
    #             thumb_label.setText("❌")
    #     else:
    #         print("❌ 썸네일 파일이 존재하지 않습니다:", data['thumbnail'])
    #         thumb_label.setText("❌")

    #     self.table.setColumnWidth(1, 120)
    #     self.table.setCellWidget(row, 1, thumb_label)

    #     # 나머지 데이터
    #     self.table.setItem(row, 2, QTableWidgetItem(data['roll']))
    #     self.table.setItem(row, 3, QTableWidgetItem(data['shot_name']))
    #     self.table.setItem(row, 4, QTableWidgetItem(data['version']))
    #     self.table.setItem(row, 5, QTableWidgetItem(data['type']))
    #     self.table.setItem(row, 6, QTableWidgetItem(data['path']))
    def add_table_row(self, data, row=None):
        if row is None:
            row = self.table.rowCount()
        self.table.insertRow(row)

        # CheckBox
        checkbox = QCheckBox()
        self.table.setCellWidget(row, 0, checkbox)

        # 썸네일 셀 (예시)
        thumb_label = QLabel()
        pixmap = QPixmap(data["thumbnail"])
        if not pixmap.isNull():
            thumb_label.setPixmap(pixmap.scaled(100, 60))
            thumb_label.setToolTip(data["thumbnail"])
        else:
            thumb_label.setText("❌")
        self.table.setCellWidget(row, 1, thumb_label)
        thumb_label.setToolTip(data["thumbnail"]) 

        # 나머지 데이터
        self.table.setItem(row, 2, QTableWidgetItem(data["roll"]))
        self.table.setItem(row, 3, QTableWidgetItem(data["shot_name"]))
        self.table.setItem(row, 4, QTableWidgetItem(data["version"]))
        self.table.setItem(row, 5, QTableWidgetItem(data["type"]))
        self.table.setItem(row, 6, QTableWidgetItem(data["path"]))
