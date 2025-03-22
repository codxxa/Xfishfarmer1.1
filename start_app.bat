
@echo off
start python main.py
timeout /t 5
start http://127.0.0.1:5000
