from shotgun_api3 import Shotgun
import os
from model.converter import find_thumbnail_from_montage
from model.excel_manager import load_excel_data

def connect_to_shotgrid():
    SERVER_PATH = "https://ww5th.shotgrid.autodesk.com"
    SCRIPT_NAME = "serin_api"         # 너가 만든 이름
    SCRIPT_KEY = "ih)kae8wxibufuLwjfwxnypey"  # 생성된 API 키

    sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    print(" ShotGrid 로그인 성공!")
    return sg

# 샷그리드 

def list_projects(sg):
    """
    ShotGrid 프로젝트 목록 반환
    """
    return sg.find("Project", [], ["name"])


def find_shot(sg, project_name, shot_name):
    # 1. 프로젝트 찾기
    project = sg.find_one("Project", [["name", "is", project_name]], ["id"])
    if not project:
        print(f" 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        return None, None

    # 2. 샷 찾기
    shot = sg.find_one("Shot", [
        ["project", "is", project],
        ["code", "is", shot_name]
    ], ["id", "code"])

    return project, shot


#test
def create_shot(sg, project, shot_name, thumbnail_path=None):
    """
    Shot이 존재하지 않을 경우 자동 생성 + 썸네일 등록
    """
    sequence_name = shot_name.split("_")[0]  # 예: S002_SH0010 → S002
    sequence = get_or_create_sequence(sg, project, sequence_name)

    data = {
        "project": project,
        "code": shot_name,
        "sg_sequence": sequence,
        "description": "자동 생성된 샷"
    }

    new_shot = sg.create("Shot", data)
    print(f" 샷 자동 생성됨: {new_shot['code']} (ID: {new_shot['id']})")

    # 썸네일이 있으면 Shot에도 업로드
    if thumbnail_path and os.path.exists(thumbnail_path):
        sg.upload_thumbnail("Shot", new_shot["id"], thumbnail_path)
        print(f"🖼 샷 썸네일 업로드 완료: {os.path.basename(thumbnail_path)}")
    else:
        print("❌ 썸네일 업로드 실패")
        if thumbnail_path is None:
            print("📛 thumbnail_path = None (썸네일 경로가 전달되지 않음)")
        else:
            print(f"📁 전달된 경로: {thumbnail_path}")
            print(f"📁 경로 존재 여부: {os.path.exists(thumbnail_path)}")
            if not os.path.exists(thumbnail_path):
                print("📛 경로는 있으나 실제 파일이 존재하지 않음")
    return new_shot


# 시퀀스 자동생성
def get_or_create_sequence(sg, project, sequence_name):
    seq = sg.find_one("Sequence", [
        ["project", "is", project],
        ["code", "is", sequence_name]
    ], ["id"])
    if seq:
        return seq
    # 없으면 생성
    return sg.create("Sequence", {
        "project": project,
        "code": sequence_name,
        "description": "자동 생성된 시퀀스"
    })

# 3. 샷그리드 찾기
def create_version(sg, project, shot, version_name, mp4_path=None, thumbnail_path=None):
    data = {
        "project": project,
        "entity": shot,
        "code": version_name,
        "description": "ScanData Auto Upload",
    }

    # 1. Version 엔티티 생성
    version = sg.create("Version", data)
    print(f" Version 생성: {version['id']}")

    # 2. 미디어 업로드 (mp4)
    if mp4_path and os.path.exists(mp4_path):
        sg.upload("Version", version["id"], mp4_path, field_name="uploaded_movie")
        print(f"🎞 mp4 업로드 완료: {os.path.basename(mp4_path)}")

    # 3. 썸네일 업로드
    if thumbnail_path and os.path.exists(thumbnail_path):
        sg.upload_thumbnail("Version", version["id"], thumbnail_path)
        sg.upload_thumbnail("Shot", shot["id"], thumbnail_path)
        print(f"🖼 썸네일 업로드 완료: {os.path.basename(thumbnail_path)}")

    return version




sg = connect_to_shotgrid()
projects = sg.find("Project", [], ["name", "id"])
for p in projects:
    print(p)