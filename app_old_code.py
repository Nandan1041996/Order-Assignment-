# Necessary Imports

import shutil
import zipfile
import io
import secrets
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename
from order import order_assignment_func
from flask import Flask, request, flash, redirect, send_file, render_template, url_for,jsonify
from exception import DataNotAvailable


# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Set logging level to ERROR or higher
handler = logging.FileHandler('error.log')  # Log errors to a file
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


app = Flask(__name__, template_folder='templates')

app.secret_key = secrets.token_hex(16)


# upload filder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


# Define a global variable to store result_df1
result_df1 = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        global result_df1  # Access the global variable
        
        if 'pending_order_file' not in request.files or 'rate_file' not in request.files or 'stock_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
   
        pending_order_file = request.files['pending_order_file']
        rate_file = request.files['rate_file']
        stock_file = request.files['stock_file']
   
        if not (allowed_file(pending_order_file.filename) and allowed_file(rate_file.filename) and allowed_file(stock_file.filename)):
            flash('Invalid file format. Please upload Excel files only.')
            return redirect(request.url)

        filename1 = secure_filename(pending_order_file.filename)
        filename2 = secure_filename(rate_file.filename)
        filename3 = secure_filename(stock_file.filename)

        pending_order_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        rate_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        stock_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))

        file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        file_path3 = os.path.join(app.config['UPLOAD_FOLDER'], filename3)

        result_df1, result_df2, rate_stck_df_c1 = order_assignment_func(file_path1, file_path2, file_path3)

        if not isinstance(result_df1,pd.DataFrame):
            return render_template('error_page.html', error_message=str(result_df1))
        
        else:
            # Extract unique Sales Order values from result_df1
            unique_sales_orders = [int(i) for i in result_df1['Salse Order'].unique()]

            # Save DataFrames to Excel files
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], 'order_with_route.xlsx')
            file3_path = os.path.join(app.config['UPLOAD_FOLDER'], 'order_route_not_found.xlsx')

            result_df1.to_excel(file1_path, index=False)
            result_df2.to_excel(file3_path, index=False)
            rate_stck_df_c1.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], 'updated_stock_file.xlsx'), index=False)

            # Create a zip archive containing all Excel files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(file1_path, os.path.basename(file1_path))
                zip_file.write(file3_path, os.path.basename(file3_path))
            zip_buffer.seek(0)

            # Remove all files from the uploads folder except the necessary ones
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename not in ('updated_stock_file.xlsx', 'order_route_not_found.xlsx', 'order_with_route.xlsx'):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")

            result_df1 = result_df1[['Salse Order', 'Sold to','Customer Name', 'order_plant', 'Plant','Plant Zone',
                         'Plant Zone Desc', 'Final Destination', 'Dest. Desc.', 'Route Name', 'Disp. Date',
                           'MODE','Material', 'Required_Stock', 'Total with STO',
                             'Proposed Level','confirm']]
            

            result_df1.rename(columns={'Sold to':'Sold To','order_plant': 'Ordered Plant', 'Plant':'Suggested Plant',
                                    'confirm':'Order Confirmed','Total with STO':'Trans Cost','Required_Stock':'Ordered Quantity'},inplace=True)

            # Pass unique_sales_orders and result_df1 to result_page.html
            return render_template('result_page.html', sales_orders=unique_sales_orders, result_df=result_df1)
        
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return jsonify({'error': 'Please ensure that your uploaded files include all columns show in Order Assignment Page.'}), 500
 

@app.route('/process_orders', methods=['GET'])
def process_orders():
    try:
        global result_df1  # Access the global variable
    
        selected_orders = request.args.get('orders')
        
        if not selected_orders:
            return "No sales orders selected."

        # Split selected orders into a list
        selected_orders = selected_orders.split(',')
        selected_orders = [float(i) for i in selected_orders]
        
        # Process selected orders using result_df1
        if result_df1 is not None:
            filtered_df = result_df1[result_df1['Salse Order'].isin(selected_orders)]
            #  Reset index starting from 1
            filtered_df.reset_index(drop=True, inplace=True)
            filtered_df.index = filtered_df.index + 1
             # Save DataFrame to CSV
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Selected Orders.csv')
            filtered_df.to_csv(csv_path, index=False)
            
            # Render the template with the filtered DataFrame
            return render_template('result_display.html', filtered_df=filtered_df.to_html(classes='table table-striped'))
        else:
            raise DataNotAvailable()
    
    except (DataNotAvailable) as e:
        logger.error(f"Exception occurred: {str(e)}")
        return render_template(f'''error_page.html', error_message={e}''')
    
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return jsonify({'error': 'Data Not Found.'}), 500
 
    
@app.route('/download_csv_trigger', methods=['GET'])
def download_csv_trigger():
    # Trigger the download of the CSV file
    return redirect(url_for('download_csv'))

@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Selected Orders.csv')
        if os.path.exists(csv_path):
            return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='Selected Orders.csv')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
