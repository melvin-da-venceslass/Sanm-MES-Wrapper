#!/bin/sh
set -x
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate fastapi_servers
pip install -r requirements.txt
python -u main.py prod
