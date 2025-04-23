from shotgun_api3 import Shotgun
import os

#  ShotGrid 로그인
def connect_to_shotgrid():
    SERVER_PATH = "https://ww5th.shotgrid.autodesk.com"
    SCRIPT_NAME = "serin_api"         # 너가 만든 이름
    SCRIPT_KEY = "ih)kae8wxibufuLwjfwxnypey"  # 생성된 API 키

    sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    print("ShotGrid 로그인 성공!")
    return sg

# 프로젝트/샷 조회
def find_shot(sg, project_name, shot_name):
    project = sg.find_one("Project", [["name", "is", project_name]], ["id"])
    shot = sg.find_one("Shot", [["project", "is", project], ["code", "is", shot_name]], ["id"])
    return project, shot



# Version 생성 및 업로드
def create_version(sg, project, shot, version_name, mp4_path=None, thumbnail_path=None):
    data = {
        "project": project,
        "entity": shot,
        "code": version_name,
        "description": "ScanData Auto Upload"
    }

    version = sg.create("Version", data)
    print(f"Version 생성 완료: ID {version['id']}")

    if mp4_path and os.path.exists(mp4_path):
        sg.upload("Version", version["id"], mp4_path, field_name="sg_uploaded_movie")
        print("🎞 MP4 업로드 완료")

    if thumbnail_path and os.path.exists(thumbnail_path):
        sg.upload_thumbnail("Version", version["id"], thumbnail_path)
        print("🖼 썸네일 업로드 완료")

    return version

# 테스트 실행
if __name__ == "__main__":
    sg = connect_to_shotgrid()

    # ShotGrid 프로젝트명 / 샷명 / 파일경로 입력
    project_name = "serin_converter"
    shot_name = "S002_SH0030"
    mp4_path = "/home/rapa/westworld_serin/converter/product/S002_SH0030/plate/sequence/v001/mp4/S002_SH0030_plate_v001.mp4"
    thumbnail_path = "/home/rapa/westworld_serin/converter/product/S002_SH0030/plate/sequence/v001/montage/S002_SH0030_montage_0001.jpg"

    project, shot = find_shot(sg, project_name, shot_name)

    if project and shot:
        create_version(sg, project, shot, mp4_path, thumbnail_path)
    else:
        print("프로젝트 또는 샷을 찾을 수 없습니다.")
