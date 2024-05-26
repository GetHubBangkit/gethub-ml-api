
uvicorn main:app --reload --port 8100
pip list

# build docker
buat DockerFile

docker build -t capstonetes .
docker run -d -p 8100:8100 capstonetes

pip install --no-cache-dir -r requirements.txt

pip freeze > requirements.txt
pip uninstall -r requirements.txt -y
rm requirements.txt

Anaconda :
Python 3.9.19

git lfs install
git lfs track "data/sentiment/model.keras"
git add .gitattributes
git commit -m "Track large files with Git LFS"
git rm --cached data/sentiment/model.keras
git add data/sentiment/model.keras
git commit -m "Add large file with Git LFS"
git push -u origin main
