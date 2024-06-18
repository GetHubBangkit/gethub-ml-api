Gethub Machine Learning API

# Download Model Sentiment Analisis
https://drive.google.com/file/d/1eVwvhv13A2ZZCveooU11aEK7LqrdJU9h/view?usp=sharing
lalu pindahkan ke folder data/sentiment

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




