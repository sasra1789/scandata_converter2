
import os
import re
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage

def get_next_versioned_filename(base_path, prefix="scanlist", ext=".xlsx"):
    """
    기존 파일을 기준으로 다음 버전명을 자동 생성
    예: scanlist_v001.xlsx → scanlist_v002.xlsx
    """
    dir_name = os.path.dirname(base_path)
    base_name = os.path.splitext(os.path.basename(base_path))[0]

    # 파일명에서 prefix_v### 형식 추출
    pattern = re.compile(rf"{re.escape(prefix)}_v(\d{{3}})")
    existing_versions = []

    for f in os.listdir(dir_name):
        match = pattern.match(f)
        if match:
            existing_versions.append(int(match.group(1)))

    next_version = max(existing_versions, default=0) + 1
    return os.path.join(dir_name, f"{prefix}_v{next_version:03d}{ext}")

def save_to_excel_with_thumbnails(data_list, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "ScanList"

    # Step 1: 컬럼 헤더 작성
    headers = ["Thumbnail", "Roll", "Shot Name", "Version", "Type", "Path"]
    ws.append(headers)

    # Step 2: 데이터 삽입
    for row_data in data_list:
        img_path = row_data["thumbnail"]

        # 텍스트 데이터만 먼저 삽입
        row = [
            "",  # 썸네일은 이미지로 삽입할 예정
            row_data["roll"],
            row_data["shot_name"],
            row_data["version"],
            row_data["type"],
            row_data["path"],
        ]
        ws.append(row)

        # Step 3: 이미지 삽입
        if img_path and os.path.exists(img_path):
            try:
                img = XLImage(img_path)
                img.width = 100
                img.height = 60
                cell = f"A{ws.max_row}"  # 현재 행의 A열에 이미지 삽입
                ws.add_image(img, cell)
                # 행 높이도 이미지에 맞게 조절
                ws.row_dimensions[ws.max_row].height = 45
            except Exception as e:
                print(f"❌ 이미지 삽입 실패: {img_path}\n{e}")

    # Step 4: 저장
    try:
        wb.save(output_path)
        print(f" 엑셀 저장 완료: {output_path}")
    except Exception as e:
        print(f"❌ 엑셀 저장 실패: {e}")



def load_excel_data(xlsx_path):
    """
    저장된 .xlsx 파일을 열어 딕셔너리 리스트로 반환
    """
    wb = load_workbook(xlsx_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    data_list = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        row_data = dict(zip(headers, row))
        data_list.append(row_data)

    return data_list



def get_next_versioned_filename(base_path):
    base_dir = os.path.dirname(base_path)
    base_name = os.path.splitext(os.path.basename(base_path))[0]  # scanlist
    ext = os.path.splitext(base_path)[1]  # .xlsx

    version = 1
    while True:
        filename = f"{base_name}_v{version:03d}{ext}"
        full_path = os.path.join(base_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1