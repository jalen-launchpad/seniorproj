import os
import cv2
from app import app, db
import urllib.request
from flask import Flask, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
import torch
from dvt import VideoBatchInput, DiffAnnotator, DVTOutput, CutAggregator
from record import Record
from record_cuts import RecordCuts
from sklearn import tree

@app.route('/')
def select_mode():
    return render_template('selectMode.html')

@app.route('/upload')
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
    records_by_username = Record.query.filter_by(account_username=username)
    records_by_username_and_filename = records_by_username.filter_by(filename=filename)
    if records_by_username_and_filename.count() == 0:
        return True
    return False

@app.route('/train', methods=['POST'])
def upload_video():
    print("made it here 1")
    if check_file_validity() and verify_params():

        print("made it here 2")
        print(request.form.keys())
        username = request.form['username']
        print("made it here 3")

        success_level = request.form['success_level']
 
        file = request.files['file']

        filename = secure_filename(file.filename)
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("made it here 4")

        if not verify_database(username, filename):
            print("made it here 5")
            return Response("A record already exists with specified username and filename", status=409,)
        file.save(fullpath)
        cuts = extract_cuts(fullpath)
        print(cuts)
        num_cuts = len(cuts.index)
        extract_first_frame(fullpath)        
        print("made it here 6")

        os.remove(fullpath)
        print('upload_video filename: ' + filename)

        record = Record(account_username=request.form['username'], filename=filename, num_cuts=len(cuts), success_level=success_level)
        for cut in cuts.iterrows():
            record_cuts = RecordCuts(account_username=request.form['username'], filename=filename, start_timestamp = int(cut[1]['frame_start']), end_timestamp = int(cut[1]['frame_end']))
            db.session.add(record_cuts)
        db.session.add(record)
        db.session.commit()

        print("made it here 7")

        return render_template('upload.html')
    else:
        print("made it here 8")

        print("Error")
        return "error"

@app.route('/analysis', methods=['POST'])
def analyze_video():
    username = request.form['username']
    file = request.files['file']
    filename = secure_filename(file.filename)
    fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not verify_database(username, filename):
        print("made it here 55!!!")
        return Response("A record already exists with specified username and filename", status=409,)
    file.save(fullpath)
    cuts = extract_cuts(fullpath)
    num_cuts = len(cuts.index)
    print("made it here 4!!!")

    os.remove(fullpath)
    print('upload_video filename: ' + filename)

    print("made it here 5!!!")
    label_vector = ['low', 'medium', 'low', 'high']
    feature_vector = [[3], [4], [2], [7]]
    classifier = tree.DecisionTreeClassifier()
    classifier = classifier.fit(feature_vector, label_vector)
    print(str(classifier.predict([[num_cuts]])))
    dot_data = tree.export_graphviz(classifier, out_file=None)
    # graph = graphviz.Source(dot_data)
    # graph.render("Silliman")

# tree.plot_tree(classifier)

    return cuts.to_json()



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