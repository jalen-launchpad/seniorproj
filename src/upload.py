import os
import cv2
from app import app, db
import urllib.request
from flask import Flask, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
import torch
from dvt import VideoBatchInput, DiffAnnotator, DVTOutput, CutAggregator
from record import Record

@app.route('/')
def upload_form():
    return render_template('upload.html')

def check_file_validity():
    if 'file' not in request.files:
        print('file validity failed')
        return False
    file = request.files['file']
    if file.filename == '':
        print('file validity failed')
        return False
    return True


def verify_params():
    form_data = request.form
    if 'username' in form_data:
        return True
    print('verify_params failed')
    return False

def verify_database(username, filename):
    records_by_username = Record.query.filter_by(account_username='jalengabbidon')
    records_by_username.filter_by(filename=filename)
    if records_by_username.count() <= 1:
        return True
    return False

@app.route('/', methods=['POST'])
def upload_video():

    if check_file_validity() and verify_params():
        username = request.form['username']
        file = request.files['file']
        filename = secure_filename(file.filename)
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not verify_database(username, filename):
            return Response("A record already exists with specified username and filename", status=409,)
        file.save(fullpath)
        cuts = extract_cuts(fullpath)
        num_cuts = len(cuts.index)
        extract_first_frame(fullpath)        


        os.remove(fullpath)
        print('upload_video filename: ' + filename)

        record = Record(account_username=request.form['username'], filename=filename, num_cuts=len(cuts))
        db.session.add(record)
        db.session.commit()

        return cuts.to_json()
    else:
        print("Error")
        return "error"


def extract_cuts(fullpath):
    vi = VideoBatchInput(input_path=fullpath)
    anno = DiffAnnotator(quantiles=[40])
    output = DVTOutput()
    while not vi.finished:
        batch = vi.next_batch()
        output.add_annotation(anno.annotate(batch))
    output.get_dataframes()["diff"]
    ca = CutAggregator(cut_vals={"q40": 5})
    diff = output.get_dataframes()['diff']
    cuts = ca.aggregate(diff)
    return cuts


def extract_first_frame(fullpath):
    vidcap = cv2.VideoCapture(fullpath)
    success, image = vidcap.read()    
    cv2.imwrite(app.config['UPLOAD_FOLDER'] + "test.jpg", image)


@app.route('/display/<filename>')
def display_video(filename):
    #print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)