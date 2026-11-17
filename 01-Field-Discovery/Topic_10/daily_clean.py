import os, time, datetime, subprocess

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "清理运行日志.log")
MAX_AGE_DAYS = 30
TEMP_DIR = os.path.join(os.environ.get("TEMP", r"C:\Users\LIUJUN~1\AppData\Local\Temp"))
CLEAN_TEMP = False  # 仅清回收站，临时文件默认关

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} {msg}\n")
    print(msg)

start_time = time.time()
log("="*50)
log(f"每日清理脚本启动 @ {datetime.datetime.now()}")
log("="*50)

# 1. 清空回收站（系统接口，安全）
try:
    log("[1/2] 清空回收站...")
    subprocess.run(["powershell.exe", "-Command", "Clear-RecycleBin -DriveLetter C,D,E,F -Force"], 
                    check=False, shell=True)
    log("  回收站已清空（或无需清理）")
except Exception as e:
    log(f"  回收站清理异常: {e}")

# 2. 临时文件（超30天，可选）
if CLEAN_TEMP:
    log(f"[2/2] 清理临时目录(超{MAX_AGE_DAYS}天): {TEMP_DIR}")
    # ...（保持原30天/跳过占用逻辑，此处省略，与原脚本一致）
else:
    log("[2/2] 临时目录清理已关闭（CLEAN_TEMP=False）")

elapsed = time.time() - start_time
log(f"总耗时: {elapsed:.2f}秒")
log("="*50 + "\n")