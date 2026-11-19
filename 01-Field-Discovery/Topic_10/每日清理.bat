@echo off
chcp 65001 >nul
::这个是放解析器的地方,我用的是绝对路径(下面那个也是)
set PY="D:\Apps___RuanJian\python\.venv\Scripts\python.exe"
::这个是放置daily_clean.py文件的路径
set DIR="D:\liujunhao.Github\ICEC-2026-0140-liujunhao\01-Field-Discovery\Topic_10"
set SCRIPT=daily_clean.py

cd /d %DIR%
if exist %PY% (
    %PY% %SCRIPT%
) else (
    echo [错误] 找不到虚拟环境Python，请检查路径！
    pause
)
pauses