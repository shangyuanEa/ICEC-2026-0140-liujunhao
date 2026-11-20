import os
from pydub import AudioSegment

# 基于脚本位置定位目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# 自动创建输出目录
os.makedirs(PROCESSED_DIR, exist_ok=True)

def main():
    for fname in sorted(os.listdir(RAW_DIR)):
        if not fname.lower().endswith(".m4a"):
            continue
        base = os.path.splitext(fname)[0]
        out_wav = os.path.join(PROCESSED_DIR, base + ".wav")
        
        # 核心防重转逻辑：如果wav已存在，直接跳过
        if os.path.isfile(out_wav):
            print(f"[跳过] 已存在: {out_wav}")
            continue
            
        print(f"[转换] {fname} -> {base}.wav")
        audio = AudioSegment.from_file(os.path.join(RAW_DIR, fname), format="m4a")
        # 统一格式：44100Hz，单声道，PCM 16bit
        audio = audio.set_frame_rate(44100).set_channels(1)
        audio.export(out_wav, format="wav", parameters=["-acodec", "pcm_s16le"])

    print("全部处理完毕！")

if __name__ == "__main__":
    main()