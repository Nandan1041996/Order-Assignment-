import os
import pandas as pd
import numpy as np
import logging
import secrets
from werkzeug.utils import secure_filename
from functions import fraight_rate_calculation
from flask import Flask, request, flash, redirect, send_file, render_template, url_for,jsonify

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Set logging level to ERROR or higher
handler = logging.FileHandler('error.log')  # Log errors to a file
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

result_df = None

@app.route('/upload_files', methods=['POST'])
def upload_files():

    global result_df

    if 'current_fraight_file' not in request.files or \
       'destination_fraight_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    current_fraight_file = request.files['current_fraight_file']
    destination_fraight_file = request.files['destination_fraight_file']
    perc_increase = request.form.get('perc_increase')

    if not (allowed_file(current_fraight_file.filename) and allowed_file(destination_fraight_file.filename)):
        flash('Invalid file format. Please upload Excel files only.')
        return redirect(request.url)

    # Check if files are provided
    if current_fraight_file.filename == '' or destination_fraight_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename1 = secure_filename(current_fraight_file.filename)
    filename2 = secure_filename(destination_fraight_file.filename)

    current_fraight_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    destination_fraight_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

    file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
    file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

    # Process percentage increase (optional)
    if perc_increase:
        perc_increase = float(perc_increase)

    result_df = fraight_rate_calculation(file_path1, file_path2, perc_increase)
    print(result_df.columns)
    result_df = result_df[['Plant','Dest. Desc.','Final Destination','MODE','Distance in KM','Direct Road Freight','Per Km Price','Proposed Price /KM','Diff B/W Old And Propose Rate',
                           'Proposed Price','Market Freight']]
    
    result_df.reset_index(drop=True,inplace=True)
    result_df.index = result_df.index+1
     # Save DataFrame to CSV
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Freight_Rate.csv')
    result_df.to_csv(csv_path, index=False)


    if not isinstance(result_df,pd.DataFrame):
        return  render_template('error_page.html', error_message=str(result_df))
    
    else:
        for file in [file_path1,file_path2]:
            os.remove(file)
        # Render the template with the filtered DataFrame
        return render_template('result_display.html', filtered_df=result_df.to_html(classes='table table-striped'))


@app.route('/download_csv_trigger', methods=['GET'])
def download_csv_trigger():
    # Trigger the download of the CSV file
    return redirect(url_for('download_csv'))


@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Freight_Rate.csv')
        if os.path.exists(csv_path):
            return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='Freight_Rate.csv')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)



