
import os
import subprocess

def convert_exr_to_jpg_with_ffmpeg(exr_path, output_path):
    """
    ffmpeg를 이용해 EXR 이미지 1장을 JPG로 변환
    :param exr_path: 원본 EXR 파일 경로
    :param output_path: 변환된 JPG 경로
    :return: 성공 여부 (True/False)
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            "ffmpeg",
            "-y",                   # 덮어쓰기 허용
            "-i", exr_path,
            "-frames:v", "1",       # 한 프레임만
            "-q:v", "2",            # 화질 (1~31, 1이 가장 좋음)
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[ffmpeg 변환 실패] {exr_path} → {output_path}\n{e}")
        return False
    
#  .mov만 썸네일 따로 생성 
def generate_mov_thumbnail(mov_path, output_dir):
    """
    MOV 파일의 첫 프레임을 JPG 썸네일로 추출
    :param mov_path: 원본 MOV 파일 경로
    :param output_dir: 저장할 경로
    :return: 썸네일 이미지 경로
    """
    if not os.path.exists(mov_path):
        return None

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(mov_path))[0]
    thumb_path = os.path.join(output_dir, f"{base_name}_thumb.jpg")

    cmd = [
        "ffmpeg",
        "-i", mov_path,
        "-ss", "00:00:00.000",
        "-vframes", "1",
        "-q:v", "2",  # 화질
        thumb_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return thumb_path
    except subprocess.CalledProcessError:
        print(f"[에러] 썸네일 생성 실패: {mov_path}")
        return None
    

def convert_to_mp4(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def convert_to_webm(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libvpx-vp9",
        "-b:v", "1M",
        "-c:a", "libopus",
        output_path
    ]
    print ("webm 변환 성공")
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def generate_montage(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "select='not(mod(n\\,5))',scale=320:180",
        "-frames:v", "5",
        output_path
    ]

    print("montage 변환 성공")
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

# 샷그리드 내에서 썸네일을 montage 폴더에서 찾기
def find_thumbnail_from_montage(dir_path):
    """
    montage 폴더에서 가장 먼저 나오는 jpg를 썸네일로 사용
    """
    if not os.path.exists(dir_path):
        return None

    files = sorted([
        f for f in os.listdir(dir_path)
        if f.lower().endswith(".jpg")
    ])
    print(f"[찾은 썸네일] {files}") 
    if not files:
        print(f"{files} 존재하지 않음!")
        return None
        

    return os.path.join(dir_path, files[0])

def generate_montage_multi(input_path, output_dir, basename, interval=10, max_frames=5):
    """
    영상 or 이미지 시퀀스에서 여러 프레임을 추출하여 개별 jpg로 저장
    :param input_path: 입력 mov 또는 exr
    :param output_dir: 저장할 폴더
    :param basename: 파일 이름 앞에 붙일 샷 이름 등
    :param interval: 몇 프레임마다 1장 추출할지
    :param max_frames: 몇 장까지 추출할지 제한
    """
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, f"{basename}_montage_%04d.jpg")

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"select='not(mod(n\\,{interval}))',scale=320:180",
        "-vsync", "vfr",
        "-frames:v", str(max_frames),
        output_template
    ]

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0