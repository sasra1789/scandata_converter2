from shotgun_api3 import Shotgun

def connect_to_shotgrid():
    SERVER_PATH = "https://ww5th.shotgrid.autodesk.com"
    SCRIPT_NAME = "serin_api"         # 너가 만든 이름
    SCRIPT_KEY = "ih)kae8wxibufuLwjfwxnypey"  # 생성된 API 키

    sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    print(" ShotGrid 로그인 성공!")
    return sg

sg = connect_to_shotgrid()
projects = sg.find("Project", [], ["name", "id"])
for p in projects:
    print(p)