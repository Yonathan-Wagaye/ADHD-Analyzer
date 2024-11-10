import os
import zipfile
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
from analysis import extractParticipant, convertToDF, process_pre_expt, createTotalError, getErrors, stat_test

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'unzipped'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXTRACT_FOLDER'] = EXTRACT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

def find_base_directory(start_path):
    """
    Find the actual base directory by checking for extra nesting.
    This function handles cases where the extracted folder has redundant nesting.
    """
    contents = os.listdir(start_path)
    
    # If there's only one folder inside, assume it's the main folder and go deeper
    if len(contents) == 1 and os.path.isdir(os.path.join(start_path, contents[0])):
        # Dive into this single folder
        nested_path = os.path.join(start_path, contents[0])
        nested_contents = os.listdir(nested_path)

        # If the nested directory again has only one folder, assume it’s double nested
        if len(nested_contents) == 1 and os.path.isdir(os.path.join(nested_path, nested_contents[0])):
            return os.path.join(nested_path, nested_contents[0])  # Return the inner nested directory

        # If the nested path has the correct structure, return it
        return nested_path
    
    # Otherwise, return the original start_path if no extra nesting is detected
    return start_path

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    # Save the uploaded file
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(zip_path)

    # Extract the zip file
    extract_path = os.path.join(app.config['EXTRACT_FOLDER'], os.path.splitext(file.filename)[0])
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Determine the actual base directory
    baseDir = find_base_directory(extract_path)
    print(baseDir)
    baseDir += '/RawData'

    # Run the analysis using the determined baseDir
    try:
        result_A = convertToDF(extractParticipant(baseDir, 1, 35, 1, 2))
        result_B = convertToDF(extractParticipant(baseDir, 1, 35, 1, 4))
        result_C = convertToDF(extractParticipant(baseDir, 1, 35, 1, 6))
        result_D = convertToDF(extractParticipant(baseDir, 1, 35, 1, 8))

        # Load and process pre-experiment data
        pre_expt_file_path = os.path.join(baseDir, 'Pre-Experiment Questionnaire-Final.csv')
        pre_expt_df = process_pre_expt(pre_expt_file_path)

        # Merge results
        final_A = createTotalError(pd.merge(pre_expt_df, result_A, on='Participant number:'))
        final_B = createTotalError(pd.merge(pre_expt_df, result_B, on='Participant number:'))
        final_C = createTotalError(pd.merge(pre_expt_df, result_C, on='Participant number:'))
        final_D = createTotalError(pd.merge(pre_expt_df, result_D, on='Participant number:'))

        # Statistical analysis
        error_A = getErrors(final_A)
        t_stat, p_val = stat_test(error_A['total_errors_adhd'], error_A['total_errors_non_adhd'])
        stats_results = {"ADHD vs Non-ADHD total errors A": {"t_statistic": t_stat, "p_value": p_val}}

        # Repeat for other datasets as needed, and add to stats_results

        return jsonify({"message": "File processed successfully", "stats": stats_results})
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
