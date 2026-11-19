import os
import subprocess

# ffmpeg 绝对路径
ffmpeg_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe")

BASE_DIR = r"D:\liujunhao.Github\ICEC-2026-0140-liujunhao\02-20Days-Challenge"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# 创建输出文件夹
if not os.path.exists(PROCESSED_DIR):
    os.makedirs(PROCESSED_DIR)

print(f"ffmpeg 路径: {ffmpeg_path}")
print(f"原始文件夹: {RAW_DIR}")
print(f"输出文件夹: {PROCESSED_DIR}")
print("=" * 50)

# 遍历转换
for file in sorted(os.listdir(RAW_DIR)):
    if file.lower().endswith(".m4a"):
        m4a_path = os.path.join(RAW_DIR, file)
        wav_path = os.path.join(PROCESSED_DIR, file.replace(".m4a", ".wav"))
        
        print(f"正在转换: {file}")
        
        # 直接用 ffmpeg 命令行：转 44100Hz / 单声道 / 16bit PCM
        cmd = [
            ffmpeg_path,
            "-i", m4a_path,
            "-ar", "44100",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            "-y",  # 覆盖已存在文件
            wav_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        
        if result.returncode == 0:
            print(f"  ✓ 成功: {os.path.basename(wav_path)}")
        else:
            print(f"  ✗ 失败: {file}")
            print(f"    错误信息: {result.stderr[-200:]}")  # 打印最后200字符的错误

print("=" * 50)
print("全部转换完成！")