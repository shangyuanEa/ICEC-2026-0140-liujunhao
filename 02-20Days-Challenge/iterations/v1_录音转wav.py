import os
from pydub import AudioSegment

# 基于脚本所在目录算绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def convert_m4a_to_wav():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    for file in sorted(os.listdir(RAW_DIR)):
        if file.lower().endswith(".m4a"):
            m4a_path = os.path.join(RAW_DIR, file)
            wav_filename = os.path.splitext(file)[0] + ".wav"
            wav_path = os.path.join(PROCESSED_DIR, wav_filename)

            audio = AudioSegment.from_file(m4a_path)
            audio.export(wav_path, format="wav", parameters=["-acodec", "pcm_s16le"])
            print(f"已转换: {file} -> {wav_filename}")

    print("全部转换完成！")

if __name__ == "__main__":
    convert_m4a_to_wav()