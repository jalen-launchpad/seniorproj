# TikTok predictor
The TikTok predictor is a web application that uses the Distant Viewing Toolkit in order to analyze and make predictions on TikTok video success.

The DVT is too large to run this on Heroku, so must be run locally.

## How to download requirements

Run in the terminal:
```
git clone https://github.com/jalen-launchpad/seniorproj.git
```
```
pip install -r requirements.txt
```
## How to run the application

```FLASK_APP=upload.py flask run``` from top-level directory

Navigate to https://localhost:5000

If seniorproject.db is not initialized... run these two commance  in terminal
```cp scripts/init_db.py init_db.py```
```python3 init_db.py```

init_db.py needs to be in top-level directory to work.

Link to zip file with 250 training data example videos and metadata.csv: 
https://drive.google.com/file/d/1WdaBDvedAzgIQVqBxnO833ythGYuyj5q/view?usp=sharing

## Note

Currently there is a seniorproject.db already initialized with the archive training data.  There is a folder, test_videos with example videos to run in "run_analysis" mode.

To test the batch upload, delete seniorproject.db, run ```python3 init_db.py``` in top level directory, download the training data archive from Drive link above, input that archive into the "train batch" page, and wait like an hour :D 
