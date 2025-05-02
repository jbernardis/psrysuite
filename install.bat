rename src current
mkdir current\logs
mkdir current\output
python -m venv ./venv
.\venv\Scripts\python -m pip install wheel
.\venv\Scripts\python -m pip install -r requirements.txt
cd current
..\venv\Scripts\python config\main.py --install
