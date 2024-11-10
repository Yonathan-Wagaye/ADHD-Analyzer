from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
import preliminary_preprocessor as preprocessor
import preliminary_plotter as plotter
import preliminary_stat_test as stat_test

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'unzipped'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXTRACT_FOLDER'] = EXTRACT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

# Route 1: File Upload and Preliminary Preprocessing
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(zip_path)
    extract_path = os.path.join(app.config['EXTRACT_FOLDER'], os.path.splitext(file.filename)[0])
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    baseDir = os.path.join(extract_path, file.filename[:-4])

    try:
        # Preliminary Preprocessing
        preprocessor.preprocess_and_save(baseDir)
        return jsonify({"message": "File uploaded and preprocessed successfully"}), 200
    
    except Exception as e:
        print(f'Upload: {e}')
        return jsonify({"error": str(e)}), 500


# Route 2: Generate and Return Statistical Analysis Results
@app.route('/api/analysis', methods=['GET'])
def generate_analysis():
    try:
        # Load the preprocessed data
        data = stat_test.load_accuracy_data()
        
        # Perform statistical analysis
        between_group_results = stat_test.basic_between_test(data)
        within_group_results = stat_test.basic_within_test(data)

        return jsonify({
            "message": "Statistical analysis generated successfully",
            "stats": {
                "p_value": {
                    "between_group": {
                        "title": "Between Group P-Value",
                        "data": between_group_results
                    },
                    "within_group": {
                        "title": "Within Group P-Value",
                        "data": within_group_results
                    }
                }
            }
        }), 200

    except Exception as e:
        print(f'Analysis error: {e}')
        return jsonify({"error": str(e)}), 500


# Route 3: Generate and Return Plots
@app.route('/api/plot', methods=['GET'])
def generate_plot():
    try:
        # Load the preprocessed data
        data = plotter.load_accuracy_data()
        
        # Generate plots
        same_group_plot = plotter.within_group_plot(data)
        between_group_plot = plotter.between_group_plot(data)

        response = jsonify({
            "message": "Plot generated successfully",
            "plots": [
                {
                    "title": "Same Group Plot",
                    "description": "Comparison of ADHD and Non-ADHD groups under different conditions.",
                    "plotUrl": same_group_plot
                },
                {
                    "title": "Different Group Plot",
                    "description": "Accuracy comparison between ADHD and Non-ADHD groups with and without distraction.",
                    "plotUrl": between_group_plot
                },
            ]
        }), 200

        return response

    except Exception as e:
        print(f'Plot error: {e}')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
