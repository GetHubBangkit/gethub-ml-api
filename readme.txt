Gethub Machine Learning API

# Python
Anaconda :
Python 3.9.19

# Using Fast API
uvicorn main:app --reload --port 8100
pip list

# Build docker
docker build -t gethub .
docker run -d -p 8100:8100 gethub

# For Information
pip install --no-cache-dir -r requirements.txt
pip freeze > requirements.txt
pip uninstall -r requirements.txt -y
rm requirements.txt




