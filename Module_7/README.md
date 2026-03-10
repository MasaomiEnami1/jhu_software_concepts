Markdown

# Module 7: AWS S3 to SageMaker Pipeline

## Project Overview
This project demonstrates a secure data pipeline using **Amazon Web Services (AWS)**. It automates the process of fetching educational data (`applicant_data.json`) from an **S3 bucket** and loading it into an **Amazon SageMaker** Jupyter Notebook instance using the `boto3` library.

The implementation follows security best practices by using **IAM user credentials** loaded via environment variables rather than hardcoding sensitive keys.

---

## Project Structure
```text
module_7/
├── src/
│   └── s3_fetch.py             # Core logic for Boto3 S3 operations
├── grad-cafe-pipeline.ipynb      # Jupyter Notebook executing the pipeline
├── requirements.txt              # Project dependencies
├── .env.example                  # Template for required environment variables
├── README.md                     # Project documentation and setup guide
└── screenshots/                  # Required verification screenshots
    ├── mfa.png                   # Root account MFA confirmation
    ├── dailyWork.png             # IAM user permissions verification
    ├── grad-cafe-bucket.png      # S3 bucket contents verification
    └── liveNotebook.png          # SageMaker instance "InService" status

Requirements

    Python: 3.10+

    Libraries: boto3, python-dotenv

    AWS Setup: An S3 bucket named grad-cafe containing applicant_data.json.

Setup & Installation
1. Environment Setup

Clone the repository and navigate to the project folder:
Bash

cd module_7

Install the required dependencies within your virtual environment:
Bash

pip install -r requirements.txt

2. Configure Credentials

To protect your AWS secrets, this project uses a .env file.

    Copy the template: cp .env.example .env

    Open .env and enter your IAM Access Key ID and Secret Access Key.

Note: Never commit your .env file to version control.
How to Run
Execute via Jupyter Notebook

    Open the Amazon SageMaker Console and start your notebook instance.

    Upload the module_7 folder contents to the instance.

    Open grad-cafe-pipeline.ipynb.

    Run the cells in order. The notebook will import download_s3_file from src/s3_fetch.py and download the data.

    Verify that applicant_data_SM.json appears in your local directory.

Quality Assurance (Linting)

To ensure code quality, run pylint on the source script:
Bash

pylint src/s3_fetch.py

Current Score: 10/10
Security Best Practices

    MFA: Multi-Factor Authentication is enabled on the Root account.

    Least Privilege: The dailyWork-ME IAM user is used for all operations.

    No Hardcoding: Credentials are managed via python-dotenv.

# Module 7: Cloud-Scale Microservices Deployment

## How to Run the Notebook
1. Open `grad-cafe-pipeline.ipynb` in VS Code or Jupyter.
2. Ensure `requirements.txt` dependencies are installed: `pip install -r requirements.txt`.
3. Run all cells to execute the data scraping, S3 upload, and local processing logic.
4. **Outputs:** Local data is saved to the `data/` folder, and processed results are uploaded to the S3 bucket shown in `grad-cafe-bucket.png`.

## EC2 Deployment
The application is deployed as a multi-container microservice (Flask, Worker, RabbitMQ, and PostgreSQL) on an AWS EC2 instance.
* Detailed deployment steps and troubleshooting notes are located in: `ec2/EC2_DEPLOYMENT.md`.
* The live application was verified at: `http://3.144.21.196:8080`.

## Cloud Cleanup
**Important:** To manage AWS costs and credits, all AWS resources (EC2 Instance and S3 Bucket) have been stopped or emptied following the successful capture of project screenshots.