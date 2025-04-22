
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