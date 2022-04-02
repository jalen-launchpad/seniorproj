import os
from app import app
import urllib.request
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import torch
from dvt import VideoBatchInput, DiffAnnotator, DVTOutput, CutAggregator


@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    else:

        filename = secure_filename(file.filename)
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(fullpath)

        vi = VideoBatchInput(input_path=fullpath)
        anno = DiffAnnotator(quantiles=[40])
        output = DVTOutput()

        while not vi.finished:
            batch = vi.next_batch()
            output.add_annotation(anno.annotate(batch))

        print(output)

        output.get_dataframes()["diff"]
        ca = CutAggregator(cut_vals={"q40": 5})
        diff = output.get_dataframes()['diff']
        cuts = ca.aggregate(diff)
        num_cuts = len(cuts.index)
        print(cuts)
        print(str(len(cuts.index)))

        os.remove(fullpath)
        #print('upload_video filename: ' + filename)
        return cuts.to_json()



@app.route('/display/<filename>')
def display_video(filename):
    #print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    app.run()