from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile

import preprocessor.preliminary_preprocessor as preprocessor
from preprocessor.accuracy_trendline_preprocessor import preprocess_accuracy_trend
from preprocessor.gender_accuracy_trendline_preprocessor import save_gender_accuracy_to_json
from preprocessor.gender_accuracy_stat_preprocessor import preprocess_gender_stat

from plotters.accuracy_trendline_plotter import generate_plots
from plotters.gender_acuracy_trendline_plotter import generate_gender_trendline_plot
from plotters.gender_post_expt_plotter import generate_gender_based_box_plots
from plotters.severity_dist_plotter import generate_pre_experiment_plot


from analyzer.accuracy_tendline_analyzer import analyze_accuracy_chiSquare
from analyzer.gender_accuracy_analyzer import analyze_gender_accuracy

import analyzer.preliminary_stat_test as stat_test

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'unzipped'
RESULTS_FOLDER = 'results'
PLOT_OUTPUT_FOLDER = os.path.join(RESULTS_FOLDER, 'plots')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXTRACT_FOLDER'] = EXTRACT_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER



os.makedirs(PLOT_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

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
        
        # Perform chi-square analysis

        chi_square_results = analyze_accuracy_chiSquare()

        # gender accuracy analysis
        preprocess_gender_stat("unzipped/RawData/RawData" )
        trend_analysis_results = analyze_gender_accuracy()
       
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
                },
                "trend_pvalue": {
                    "title": "Trend-Based P-Values",
                    "data": trend_analysis_results,
                },
                "chi_square": {
                    "title": "Chi-Square Analysis",
                    "data": chi_square_results
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
        # Step 1: Process general trendline plots
        baseDir = "unzipped/RawData/RawData"  # Adjust this path as needed
        preprocess_accuracy_trend(baseDir)

        # Generate trendline plots for n=12 and n=120
        trendline_plots = generate_plots()

        # Step 2: Process gender-based plots
        pre_experiment_file = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
        save_gender_accuracy_to_json(
            baseDir=baseDir,
            pre_experiment_csv=pre_experiment_file,
            output_file=os.path.join(RESULTS_FOLDER, "gender_accuracy.json"),
            n=120
        )

        # Generate gender trendline plot
        gender_plot_base64 = generate_gender_trendline_plot(os.path.join(RESULTS_FOLDER, "gender_accuracy.json"))

        # Step 3: Build the response
        response = []
        # Add trendline plots to the response
        for n, base64_plot in trendline_plots.items():
            response.append({
                "title": f"Trendline Plot ({n})",
                "description": f"Accuracy trendline for {n} blocks per session.",
                "plotUrl": base64_plot
            })

        # Add gender plot to the response
        response.append({
            "title": "Gender-Based Trendline Plot",
            "description": "Interactive trendline plot by gender and ADHD status.",
            "plotUrl": gender_plot_base64
        })

        box_plots = generate_gender_based_box_plots(
            pre_experiment_csv=os.path.join(baseDir, "Pre-Experiment Questionnaire.csv"),
            post_experiment_csv=os.path.join(baseDir, "Post-Experiment Question.csv")
        )

        # Add box plots to the response
        for group_name, base64_plot in box_plots.items():
            response.append({
                "title": f"Box Plot - {group_name.replace('_', ' ')}",
                "description": f"Box plot showing the level of distraction for {group_name.replace('_', ' ')} participants.",
                "plotUrl": base64_plot
            })
        


        pre_experiment_plot_base64 = generate_pre_experiment_plot(
            pre_experiment_csv=pre_experiment_file,
            column="ADHD Score",  # Adjust the column name based on your dataset
            title="Severity Level Distribution"
        )
        response.append({
            "title": "Severity Level Distribution Plot",
            "description": "Bar plot showing score frequencies from the pre-experiment questionnaire.",
            "plotUrl": pre_experiment_plot_base64
        })

        return jsonify({
            "message": "Plots generated successfully",
            "plots": response
        }), 200

    except Exception as e:
        print(f"Plot generation error: {e}")
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
