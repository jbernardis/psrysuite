mkdir logs
mkdir output
python -m venv ./venv
.\venv\Scripts\python -m pip install wheel
.\venv\Scripts\python -m pip install -r requirements.txt
.\venv\Scripts\python config\main.py --install
