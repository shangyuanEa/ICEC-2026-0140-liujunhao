@echo off
cd /d %~dp0
echo 正在运行转码脚本...
python v1_录音转wav.py
echo.
echo 运行结束，请查看上方信息。
pause