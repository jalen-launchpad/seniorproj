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

@app.route('/train-upload')
def train_upload_form():
    return render_template('train-upload.html')


@app.route('/run-upload')
def run_upload_form():
    return render_template('run-upload.html')

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

        record = Record(account_username=request.form['username'], filename=filename, success_level=success_level)
        for cut in cuts.iterrows():
            record_cuts = RecordCuts(account_username=request.form['username'], filename=filename, start_timestamp = int(cut[1]['frame_start']), end_timestamp = int(cut[1]['frame_end']))
            db.session.add(record_cuts)
        db.session.add(record)
        db.session.commit()

        print("made it here 7")
        

        return render_template('train-upload.html')
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
        print("made it here 55")
        return Response("A record already exists with specified username and filename", status=409,)
    file.save(fullpath)
    cuts = extract_cuts(fullpath)
    print("made it here 4")
    list_record_cuts = []
    for cut in cuts.iterrows():
        record_cuts = RecordCuts(account_username=request.form['username'], filename=filename, start_timestamp = int(cut[1]['frame_start']), end_timestamp = int(cut[1]['frame_end']))
        list_record_cuts.append(record_cuts)
    os.remove(fullpath)
    print('upload_video filename: ' + filename)

    print("made it here 5")
    label_vector = retrieve_label_vector(username)
    feature_vector = retrieve_feature_vector(username)
    
    classifier = tree.DecisionTreeClassifier()
    classifier = classifier.fit(feature_vector, label_vector)
    result = str(classifier.predict([assemble_feature_vector(list_record_cuts)]))
    print(result)
    dot_data = tree.export_graphviz(classifier, out_file=None)
    # graph = graphviz.Source(dot_data)
    # graph.render("Silliman")

    # tree.plot_tree(classifier)

    return result

def cuts_before_one_third(cuts):
    # num_cuts in first third of video
    print
    maximum = max(cuts, key=lambda x:int(x.end_timestamp))
    print(maximum.end_timestamp)
    one_third_threshold = int(maximum.end_timestamp / 3)
    cuts_before_one_third_threshold = cuts.sort(key=lambda x:x.end_timestamp < one_third_threshold)
    cuts_before_one_third_threshold = [] if cuts_before_one_third_threshold == None else cuts_before_one_third_threshold 
    cuts_before_one_third_threshold = len(cuts_before_one_third_threshold)
    return cuts_before_one_third_threshold

def cuts_in_last_third(cuts):
    # num_cuts starting in last third of video
    maximum = max(cuts, key=lambda x:int(x.end_timestamp))
    print(maximum.end_timestamp)
    one_third_threshold = int(maximum.end_timestamp * 2 / 3)
    cuts_before_one_third_threshold = cuts.sort(key=lambda x:x.start_timestamp > one_third_threshold)
    cuts_before_one_third_threshold = [] if cuts_before_one_third_threshold == None else cuts_before_one_third_threshold 
    cuts_before_one_third_threshold = len(cuts_before_one_third_threshold)
    return cuts_before_one_third_threshold

def video_duration(cuts):
    # num_cuts starting in last third of video
    maximum = max(cuts, key=lambda x:int(x.end_timestamp))
    return maximum.end_timestamp

def assemble_feature_vector(num_cuts):
    listCounts = []
    cuts_before_one_third_threshold = cuts_before_one_third(num_cuts)
    print("cuts before 1/3 " + str(cuts_before_one_third_threshold))
    cuts_in_last_third_threshold = cuts_in_last_third(num_cuts)
    duration = video_duration(num_cuts)
    listCounts.append(len(num_cuts))
    listCounts.append(cuts_before_one_third_threshold)
    listCounts.append(cuts_in_last_third_threshold)
    listCounts.append(duration)
    return listCounts

def retrieve_feature_vector(username):
    records = RecordCuts.query.filter_by(account_username=username).order_by(RecordCuts.filename.desc())
    allFilenames = records.group_by(RecordCuts.filename).order_by(RecordCuts.filename.desc()).all()
    listCounts = []
    for filename in allFilenames:
        print(filename)
        # num_cuts
        num_cuts = records.filter_by(filename=filename.filename).all()
        print("num_cuts " + str(len(num_cuts)))

        listCounts.append(assemble_feature_vector(num_cuts))
    return listCounts

    
def retrieve_label_vector(username):
    records = Record.query.filter_by(account_username=username).order_by(Record.filename.desc()).all()
    mapped = map(lambda x: x.success_level, records)
    return list(mapped)

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