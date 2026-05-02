import torch
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split

# ==========================================
# 1. REPLICATE THE TRAINING FORMATTING
# ==========================================

def create_unified_input(row):
    """
    Must match the exact logic used in train_model.py 
    to ensure the model understands the input.
    """
    def clean(val, placeholder="None"):
        if pd.isna(val) or str(val).lower() == 'nan' or str(val).strip() == "":
            return placeholder
        return str(val).strip()

    unified_text = (
        f"Program: {clean(row.get('Program'))}\n"
        f"University: {clean(row.get('University'))}\n"
        f"Comments: {clean(row.get('comments'))}\n"
        f"Term: {clean(row.get('term'))}\n"
        f"Degree: {clean(row.get('Degree'))}\n"
        f"Citizenship: {clean(row.get('US/International'))}\n"
        f"GPA: {clean(row.get('GPA'))}\n"
        f"GRE Quant: {clean(row.get('GRE'))}\n"
        f"GRE Verbal: {clean(row.get('GRE V'))}\n"
        f"GRE AW: {clean(row.get('GRE AW'))}"
    )
    return unified_text

# ==========================================
# 2. LOAD MODEL AND DATA
# ==========================================

def run_evaluation():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "./admissions_model"
    
    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    model.eval()

    # Load raw data and recreate the input column
    df = pd.read_csv("processed_admissions.csv")
    print("Recreating multimodal strings...")
    df['model_input'] = df.apply(create_unified_input, axis=1)

    # Replicate the exact 80/20 split from Section 3
    _, X_test, _, y_test = train_test_split(
        df['model_input'], df['label'], 
        test_size=0.2, random_state=42, stratify=df['label']
    )

    # ==========================================
    # 3. INFERENCE LOOP
    # ==========================================
    print(f"Running inference on {len(X_test)} test samples...")
    preds = []
    probs = []
    softmax = torch.nn.Softmax(dim=1)

    with torch.no_grad():
        for text in X_test:
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", truncation=True, 
                               max_length=128, padding=True).to(device)
            # Predict
            outputs = model(**inputs)
            
            # Calculate probabilities
            prob = softmax(outputs.logits)
            prediction = torch.argmax(prob, dim=1).item()
            
            preds.append(prediction)
            probs.append(prob[0].cpu().numpy())

    # ==========================================
    # 4. REQUIRED OUTPUTS FOR SECTION 5
    # ==========================================

    # A. Confusion Matrix
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Rejected', 'Accepted'], 
                yticklabels=['Rejected', 'Accepted'])
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.title('Admissions Prediction Confusion Matrix')
    plt.savefig('confusion_matrix.png')
    print("\n[SUCCESS] Confusion Matrix saved as 'confusion_matrix.png'")

    # B. Create a results dataframe for analysis
    results_df = pd.DataFrame({
        'text': X_test,
        'actual': y_test,
        'predicted': preds,
        'prob_rejected': [p[0] for p in probs],
        'prob_accepted': [p[1] for p in probs]
    })

    print("\n" + "="*60)
    print("SECTION 5: FINAL EVALUATION REPORT")
    print("="*60)

    # C. Metrics Table
    print("\n--- CLASSIFICATION METRICS ---")
    print(classification_report(y_test, preds, target_names=['Rejected', 'Accepted']))
    print(f"Overall Accuracy: {accuracy_score(y_test, preds):.4f}")

    # D. Probability Examples
    print("\n--- PROBABILITY EXAMPLES ---")
    for i in range(3):
        row = results_df.iloc[i]
        print(f"Sample {i+1}: Result={row['predicted']} | "
              f"P(Acc)={row['prob_accepted']:.4f} | P(Rej)={row['prob_rejected']:.4f}")

    # E. Correct vs Incorrect Examples
    correct = results_df[results_df['actual'] == results_df['predicted']]
    incorrect = results_df[results_df['actual'] != results_df['predicted']]

    print("\n--- CORRECTLY CLASSIFIED EXAMPLE ---")
    print(correct.iloc[0]['text'])
    print(f"Result: {correct.iloc[0]['predicted']} (Matches Actual)")

    print("\n--- INCORRECTLY CLASSIFIED EXAMPLE ---")
    print(incorrect.iloc[0]['text'])
    print(f"Result: {incorrect.iloc[0]['predicted']} (Actual was {incorrect.iloc[0]['actual']})")
    
    print("="*60)

if __name__ == "__main__":
    run_evaluation()