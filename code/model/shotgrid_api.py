from shotgun_api3 import Shotgun

def connect_to_shotgrid():
    SERVER_PATH = "https://ww5th.shotgrid.autodesk.com"
    SCRIPT_NAME = "serin_api"         # 너가 만든 이름
    SCRIPT_KEY = "ih)kae8wxibufuLwjfwxnypey"  # 생성된 API 키

    sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    print(" ShotGrid 로그인 성공!")
    return sg

# 샷그리드 
def find_shot(sg, project_name, shot_name):
    # 1. 프로젝트 찾기
    project = sg.find_one("Project", [["name", "is", project_name]], ["id"])
    if not project:
        print(f"❌ 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        return None, None

    # 2. 샷 찾기
    shot = sg.find_one("Shot", [
        ["project", "is", project],
        ["code", "is", shot_name]
    ], ["id", "code"])

    return project, shot


def create_shot(sg, project, shot_name):
    """
    Shot이 존재하지 않을 경우 자동 생성
    """
    data = {
        "project": project,
        "code": shot_name,
        "sg_sequence": {"type": "Shot", "name": shot_name} if shot_name else None,
        "description": "자동 생성된 샷"
    }
    new_shot = sg.create("Shot", data)
    print(f" 샷 자동 생성됨: {new_shot['code']} (ID: {new_shot['id']})")
    return new_shot


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
    print(f"✅ Version 생성: {version['id']}")

    # 2. 미디어 업로드 (mp4)
    if mp4_path and os.path.exists(mp4_path):
        sg.upload("Version", version["id"], mp4_path, field_name="uploaded_movie")
        print(f"🎞 mp4 업로드 완료: {os.path.basename(mp4_path)}")

    # 3. 썸네일 업로드
    if thumbnail_path and os.path.exists(thumbnail_path):
        sg.upload_thumbnail("Version", version["id"], thumbnail_path)
        print(f"🖼 썸네일 업로드 완료: {os.path.basename(thumbnail_path)}")

    return version

sg = connect_to_shotgrid()
projects = sg.find("Project", [], ["name", "id"])
for p in projects:
    print(p)