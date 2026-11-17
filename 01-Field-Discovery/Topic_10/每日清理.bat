@echo off
chcp 65001 >nul
set PY="D:\Apps___RuanJian\python\.venv\Scripts\python.exe"
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