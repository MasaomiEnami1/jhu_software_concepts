import pandas as pd
import numpy as np
import torch
import os
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURATION ---
MODEL_NAME = 'distilbert-base-uncased'
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 1  
LEARNING_RATE = 2e-5

# ==========================================
# SECTION 2: UNIFIED MODEL INPUT (FORMATTING)
# ==========================================

def create_unified_input(row):
    """
    Transforms each applicant row into a single text representation.
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
# PYTORCH DATASET SETUP
# ==========================================

class AdmissionsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]

        # Use the tokenizer directly (more robust than encode_plus)
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================

def main():
    # 1. Load the dataset
    if not os.path.exists("processed_admissions.csv"):
        print("Error: processed_admissions.csv not found.")
        return

    df = pd.read_csv("processed_admissions.csv")

    # 2. Section 2: Create Unified Inputs
    print("Generating unified multimodal strings...")
    df['model_input'] = df.apply(create_unified_input, axis=1)

    # 3. Section 3: Split the Data
    X_train, X_test, y_train, y_test = train_test_split(
        df['model_input'], 
        df['label'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )

    print("\n" + "="*40)
    print("SECTION 3: DATA SPLIT SUMMARY")
    print("="*40)
    print(f"Training set size: {len(X_train)} samples")
    print(f"Test set size:     {len(X_test)} samples")
    print("-" * 40)

    # 4. Initialize Tokenizer and Loaders
    # We use AutoTokenizer to handle the specific model requirements automatically
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    train_ds = AdmissionsDataset(X_train.to_numpy(), y_train.to_numpy(), tokenizer, MAX_LEN)
    test_ds = AdmissionsDataset(X_test.to_numpy(), y_test.to_numpy(), tokenizer, MAX_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    # 5. Initialize Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model = model.to(device)

    # 6. Fine-Tuning Setup
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    # 7. Training Loop
    print("\nStarting Fine-Tuning...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for i, batch in enumerate(train_loader):
            ids = batch['input_ids'].to(device)
            mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            model.zero_grad()
            outputs = model(ids, attention_mask=mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            if i % 100 == 0:
                print(f"  Batch {i}/{len(train_loader)} - Loss: {loss.item():.4f}")

        print(f"Epoch {epoch+1} complete. Avg Loss: {total_loss/len(train_loader):.4f}")

    # 8. Evaluation
    print("\nEvaluating Model...")
    model.eval()
    preds, actuals = [], []
    with torch.no_grad():
        for batch in test_loader:
            ids = batch['input_ids'].to(device)
            mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(ids, attention_mask=mask)
            _, p = torch.max(outputs.logits, dim=1)
            preds.extend(p.cpu().tolist())
            actuals.extend(labels.cpu().tolist())

    print("\n--- PERFORMANCE REPORT ---")
    print(classification_report(actuals, preds, target_names=['Rejected', 'Accepted']))

    # 9. Save
    model.save_pretrained("./admissions_model")
    tokenizer.save_pretrained("./admissions_model")
    print("\nModel saved to './admissions_model'.")

if __name__ == "__main__":
    main()