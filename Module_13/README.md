Module 13: Multimodal Graduate Admissions Predictor
Overview

This project implements a multimodal admissions classification system using a fine-tuned DistilBERT Transformer model. Unlike standard numeric classifiers, this system "reads" applicant comments and program names alongside quantitative data (GPA/GRE) to predict whether an applicant will be Accepted or Rejected. The system is deployed as a dynamic Flask web application.
Project Structure
Plaintext

Module_13/
├── admissions_model/      # Saved Weights, Tokenizer, and Config
├── templates/             # HTML templates (predict.html, result.html)
├── train_model.py         # Script to fine-tune the DistilBERT model
├── evaluation.py          # Generates Confusion Matrix and Metrics
├── inference.py           # Helper class for model prediction logic
├── run.py                 # Main Flask application script
├── processed_admissions.csv # Cleaned dataset used for training
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation

Installation & Setup
1. Create a Virtual Environment

It is highly recommended to use a virtual environment to avoid dependency conflicts.
Bash

python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on Mac/Linux:
source .venv/bin/activate

2. Install Dependencies
Bash

pip install -r requirements.txt

Usage Instructions
Step 1: Training (Optional)

The model is already saved in the admissions_model/ folder. If you wish to retrain it:
Bash

python train_model.py

Step 2: Evaluation

To generate the performance metrics and the confusion matrix:
Bash

python evaluation.py

Step 3: Launch the Web Application

Start the Flask server to access the "Will You Get In?" predictor:
Bash

python run.py

Once the server is running, navigate to:

http://127.0.0.1:5000/will-you-get-in
Model Details

    Base Model: distilbert-base-uncased

    Max Input Length: 128 tokens

    Optimizer: AdamW

    Accuracy: ~78%

    Input Format: Unified text template incorporating GPA, GRE, Program Name, and Applicant Comments.

Disclaimer

Important: This system was developed as a course project for JHU Software Concepts.

    The model is trained on self-reported data from GradCafe, which contains inherent selection bias.

    The predictions are statistical estimations and not official admissions decisions.

    This tool should not be used as a definitive authority for real-world academic planning.