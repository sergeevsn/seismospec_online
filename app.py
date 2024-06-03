import os
from flask import Flask, app, request, flash, redirect, jsonify

from flask import render_template

from utils import read_segy, get_spectrum
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

app.config['data'] = None
app.config['dt'] = 0
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DEMO_FILENAME'] = 'demo_data.sgy'
app.config['filename'] = app.config['DEMO_FILENAME']
app.config['MAX_CONTENT_LENGTH'] =  5 * 1024 * 1024 # limit uploaded file size

def load_data(fname):
        
    heatmap_z = app.config['data'].tolist()
    heatmap_x = [x for x in range(app.config['data'].shape[1])]
    heatmap_y = [y*app.config['dt']*1000 for y in range(app.config['data'].shape[0])]
    freq, spec = get_spectrum(app.config['data'], app.config['dt'])
    return heatmap_x, heatmap_y, heatmap_z, spec.tolist(), freq.tolist()

def get_heatmap_params(data, dt):
    heatmap_z = data.tolist()
    heatmap_x = [x for x in range(data.shape[1])]
    heatmap_y = [y*dt*1000 for y in range(data.shape[0])]    
    return heatmap_x, heatmap_y, heatmap_z

    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['sgy']

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/', methods=['GET', 'POST'])

def index():
    fname_to_load = app.config['DEMO_FILENAME']
    if request.method == 'POST':    
        
        file = request.files['file']        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            app.config['filename'] = secure_filename(file.filename)
            fname_to_load = 'uploaded.sgy'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname_to_load))

    app.config['data'], app.config['dt'] = read_segy(fname=os.path.join(app.config['UPLOAD_FOLDER'], fname_to_load))    
    heatmap_x, heatmap_y, heatmap_z = get_heatmap_params(app.config['data'], app.config['dt'])    
    freq, spec = get_spectrum(app.config['data'], app.config['dt'])
   
    return render_template('index.html', filename=app.config['filename'], 
                           heatmap_x=heatmap_x, heatmap_y=heatmap_y, heatmap_z=heatmap_z, spec=spec.tolist(), 
                           freq=freq.tolist(), max_file_size=app.config['MAX_CONTENT_LENGTH'])

@app.route('/spec_update', methods=['POST'])

def spec_update():
    x0, y0, x1, y1 = request.json
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    x0 = round(x0)
    x1 = round(x1)
    y0 = round(y0/app.config['dt']/1000)
    y1 = round(y1/app.config['dt']/1000)
    selected_data = app.config['data'][y0:y1+1, x0:x1+1]   
   
    heatmap_x, heatmap_y, heatmap_z = get_heatmap_params(app.config['data'], app.config['dt'])   
    freq, spec = get_spectrum(selected_data, app.config['dt'])
    context = {
        'heatmap_x': heatmap_x,
        'heatmap_y': heatmap_y,
        'heatmap_z': heatmap_z,
        'spec': spec.tolist(),
        'freq': freq.tolist(),
    }
    
    return jsonify(context)
    


if __name__ == '__main__':
    app.run(host='0.0.0.0')
