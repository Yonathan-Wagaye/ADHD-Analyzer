from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile

import preprocessor.preliminary_preprocessor as preprocessor
from preprocessor.accuracy_trendline_preprocessor import preprocess_accuracy_trend
from preprocessor.gender_accuracy_trendline_preprocessor import save_gender_accuracy_to_json
from preprocessor.gender_accuracy_stat_preprocessor import preprocess_gender_stat
from preprocessor.geneder_cumulative_stats_preprocessor import preprocess_cumulative_gender_accuracy
from preprocessor.preliminary_pose_preprocessor import preprocess_pose
from preprocessor.pose_trendline_stat_preprocessor import preprocess_pose_trendline_stats
from preprocessor.pose_gender_trendline_stat_preprocessor import preprocess_pose_stability_by_gender
from preprocessor.pose_gender_cumilative_stat_preprocessor import preprocess_cumulative_pose_stability
from preprocessor.pose_trendilne_preprocessor import preprocess_and_save_pose_trendlines
from preprocessor.pose_gender_trendline_preprocessor import preprocess_and_save_pose_trendlines_by_gender
from preprocessor.accuracy_within_session_preprocessor import preprocess_within_session_accuracy

from plotters.accuracy_trendline_plotter import generate_plots
from plotters.gender_acuracy_trendline_plotter import generate_gender_trendline_plot
from plotters.gender_post_expt_plotter import generate_gender_based_box_plots
from plotters.severity_dist_plotter import generate_gender_severity_plot
from plotters.post_expt_plotter import generate_adhd_based_box_plots
from plotters.pose_trendline_plotter import generate_pose_trendline_plots
from plotters.pose_gender_trendline_plotter import generate_pose_trendline_plots_by_gender
from plotters.accuracy_within_session_plotter import generate_within_session_box_plots

from analyzer.accuracy_tendline_analyzer import analyze_accuracy_chiSquare
from analyzer.gender_accuracy_analyzer import analyze_gender_accuracy
from analyzer.post_expt_analyzer import perform_p_value_analysis, get_participant_counts
from analyzer.gender_cumulative_stats_analyzer import analyze_cumulative_gender_accuracy
from analyzer.preliminary_pose_analyzer import analyze_pose_data
from analyzer.pose_trendline_stat_analyzer import analyze_pose_pvalues
from analyzer.pose_gender_trendline_stat_analyzer import analyze_gender_pose_pvalues
from analyzer.pose_gender_cumulative_stat_analyzer import analyze_cumulative_gender_pose_stability
from analyzer.accuracy_within_session_analyzer import analyze_within_session_accuracy


import analyzer.preliminary_stat_test as stat_test

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'unzipped'
RESULTS_FOLDER = 'results'
ACCURACY_BASE_DIR = 'unzipped/RawData/RawData/Accuracy'
POSE_BASE_DIR = 'unzipped/RawData/RawData/Pose'
BASE_DIR = 'unzipped/RawData/RawData'

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
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            baseDir = os.path.join(extract_path, file.filename[:-4])

            # Validate Accuracy folder
            accuracy_path = os.path.join(baseDir, 'Accuracy')
            if not os.path.exists(accuracy_path):
                return jsonify({"error": "Missing Accuracy folder"}), 400

            # Validate Pose folder and thresholds
            pose_path = os.path.join(baseDir, 'Pose')
            if not os.path.exists(pose_path):
                return jsonify({"error": "Missing Pose folder"}), 400

            thresholds = ['threshold_15', 'threshold_20', 'threshold_25']
            for threshold in thresholds:
                threshold_path = os.path.join(pose_path, threshold)
                if not os.path.exists(threshold_path):
                    return jsonify({"error": f"Missing {threshold} folder in Pose"}), 400

            # Preliminary Preprocessing
            preprocessor.preprocess_and_save(baseDir)

            return jsonify({"message": "File uploaded and preprocessed successfully"}), 200
        
    except Exception as e:
        print(f'Upload error: {e}')
        return jsonify({"error": str(e)}), 500


# Analysis route
@app.route('/api/analysis', methods=['GET'])
def generate_analysis():
    try:
        # Accuracy Analysis
        # ----------------------------------
        # Load preprocessed data
        data = stat_test.load_accuracy_data()
        print("Loaded accuracy data")

        # Perform statistical analysis
        between_group_results = stat_test.basic_between_test(data)
        within_group_results = stat_test.basic_within_test(data)
        print("Performed basic accuracy stat tests")

        # Chi-square analysis
        preprocess_accuracy_trend(BASE_DIR)
        chi_square_results = analyze_accuracy_chiSquare()
        print("Performed chi-square analysis")

        # Gender accuracy analysis
        preprocess_gender_stat(BASE_DIR)
        trend_analysis_results = analyze_gender_accuracy()
        print("Performed gender trend analysis")

        # Cumulative gender accuracy analysis
        preprocess_cumulative_gender_accuracy(BASE_DIR)
        cumulative_pvalues_results = analyze_cumulative_gender_accuracy()
        print("Performed cumulative gender accuracy analysis")

        # Pose Analysis
        # ----------------------------------
        preprocess_pose(BASE_DIR)  # Process pose data for threshold 15
        pose_analysis_results = analyze_pose_data()
        print("Performed pose analysis")

        # Pose Trendline Analysis
        # ----------------------------------
        preprocess_pose_trendline_stats(BASE_DIR)
        pose_trend_pvalues = analyze_pose_pvalues()
        print("Performed pose trendline analysis")

        preprocess_pose_stability_by_gender(BASE_DIR) 
        gender_pose_trend_pvalues =analyze_gender_pose_pvalues()
        print("Performed gender pose trendline analysis")

        preprocess_cumulative_pose_stability(BASE_DIR)  # Preprocess cumulative pose stability
        cumulative_pose_results = analyze_cumulative_gender_pose_stability()
        print("Performed cumulative pose stability analysis")

       


        # Build the response
        response = {
            "message": "Statistical analysis generated successfully",
            "accuracy": {
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
                },
                "cumulative_pvalues": {
                    "title": "Cumulative P-Values",
                    "data": cumulative_pvalues_results
                }
            },
            "pose": {
                "trend_pvalue": {
                    "title": "Trend-Based P-Values (Pose)",
                    "data": pose_trend_pvalues
                },
                "threshold_15": {
                    "title": "Pose Stability Analysis",
                    "data": pose_analysis_results
                },
                "gender_trend_p_value": {
                    "title": "Gender based Trendline P-values (Pose)",
                    "data":gender_pose_trend_pvalues,
                },
                "cumulative_pvalues": {
                    "title": "Cumulative Pose Stability P-Values",
                    "data": cumulative_pose_results
                }
            }
        }

        return jsonify(response), 200

    except Exception as e:
        print(f'Analysis error: {e}')
        return jsonify({"error": str(e)}), 500


    
# Route 3: Generate and Return Plots


@app.route('/api/plot', methods=['GET'])
def generate_plot():
    try:
        # Step 1: Process general trendline plots
        preprocess_accuracy_trend(BASE_DIR)

        # Generate trendline plots for n=12 and n=120
        trendline_plots = generate_plots()

        # Step 2: Process gender-based plots
        pre_experiment_file = os.path.join(BASE_DIR, "Pre-Experiment Questionnaire.csv")
        save_gender_accuracy_to_json(
            baseDir=ACCURACY_BASE_DIR,
            pre_experiment_csv=pre_experiment_file,
            output_file=os.path.join(RESULTS_FOLDER, "accuracy/gender_accuracy.json"),
            n=120
        )

        # Generate gender trendline plot
        gender_plot_base64 = generate_gender_trendline_plot(os.path.join(RESULTS_FOLDER, "accuracy/gender_accuracy.json"))

        # Step 3: Process pose trendline plots
        preprocess_and_save_pose_trendlines(BASE_DIR, num_experiments=59, num_sessions=8, threshold=15)
        pose_trendline_plots = generate_pose_trendline_plots(base_dir=os.path.join(BASE_DIR, "results"))

        preprocess_and_save_pose_trendlines_by_gender(BASE_DIR, num_experiments=59, num_sessions=8, thresholds=[15])
        gender_pose_trendline_plots = generate_pose_trendline_plots_by_gender(base_dir=os.path.join(BASE_DIR, "results"), thresholds=[15])
        print(gender_pose_trendline_plots)
        

        # Step 4: Build the response
        response = {
            "message": "Plots generated successfully",
            "accuracy_plots": [],
            "pose_plots": []
        }

        # Add accuracy trendline plots to the response
        for n, base64_plot in trendline_plots.items():
            response["accuracy_plots"].append({
                "title": f"Trendline Plot (n={n})",
                "description": f"Accuracy trendline for {n} blocks per session.",
                "plotUrl": base64_plot
            })

        # Add gender trendline plot to the response
        response["accuracy_plots"].append({
            "title": "Gender-Based Trendline Plot",
            "description": "Interactive trendline plot by gender and ADHD status.",
            "plotUrl": gender_plot_base64
        })

        # Add pose trendline plots to the response
        for key, base64_plot in pose_trendline_plots.items():
            response["pose_plots"].append({
                "title": f"Pose Stability Trendline Plot ({key})",
                "description": f"Pose stability trendline for {key}.",
                "plotUrl": base64_plot
            })

        for key, base64_plot in gender_pose_trendline_plots.items():
            response["pose_plots"].append({
                "title": f"Gender-Based Pose Trendline Plot ({key})",
                "description": f"Pose trendline for gender groups at {key}.",
                "plotUrl": base64_plot
            })

        return jsonify(response), 200

    except Exception as e:
        print(f"Plot generation error: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/api/info', methods=['GET'])
def get_expt_info():
    try:
        # Generate the severity level plot
        severity_plot_base64 = generate_gender_severity_plot(BASE_DIR)
        print('gender severity')

        # Generate the ADHD and Non-ADHD box plots
        adhd_box_plots = generate_adhd_based_box_plots(BASE_DIR)
        print('adhd box splot')

        # Generate the gender-based box plots
        gender_box_plots = generate_gender_based_box_plots(
            pre_experiment_csv=os.path.join(BASE_DIR, "Pre-Experiment Questionnaire.csv"),
            post_experiment_csv=os.path.join(BASE_DIR, "Post-Experiment Question.csv")
        )
        print('gender box plot')

        # Perform p-value analysis
        p_values = perform_p_value_analysis(BASE_DIR)
        print('p values')

        # Get participant counts
        participant_counts = get_participant_counts(BASE_DIR)
        print('partcipant info')

        # Build the response
        response = {
            "message": "Experiment info retrieved successfully",
            "participant_counts": participant_counts,
            "plots": [
                {
                    "title": "Severity Levels by Gender",
                    "description": "Stacked bar plot showing severity levels by gender.",
                    "plotUrl": severity_plot_base64
                },
                {
                    "title": "Level of Distraction - ADHD",
                    "description": "Box plot showing level of distraction for ADHD participants.",
                    "plotUrl": adhd_box_plots['ADHD']
                },
                {
                    "title": "Level of Distraction - Non-ADHD",
                    "description": "Box plot showing level of distraction for Non-ADHD participants.",
                    "plotUrl": adhd_box_plots['Non-ADHD']
                }
            ],
             "gender_box_plots": []
           
        }

        # Add gender-based box plots to the response
        for group_name, base64_plot in gender_box_plots.items():
            response["gender_box_plots"].append({
                "title": f"Box Plot - {group_name.replace('_', ' ')}",
                "description": f"Box plot showing the level of distraction for {group_name.replace('_', ' ')} participants.",
                "plotUrl": base64_plot
            })

        # Add p-values
        response["p_values"] = p_values

        return jsonify(response), 200

    except Exception as e:
        print(f"Error in /api/info: {e}")
        return jsonify({"error": str(e)}), 500


 
 

if __name__ == '__main__':
    app.run(debug=True)
