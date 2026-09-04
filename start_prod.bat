@echo off
conda run -n fastapi_servers pip install -r requirements.txt
conda run -n fastapi_servers python main.py prod
