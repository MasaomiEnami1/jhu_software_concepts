import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AdmissionsPredictor:
    def __init__(self, model_path="./admissions_model"):
        # Load once to save memory and time
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def predict(self, data):
        # 1. Format exactly like the training data
        # Use .get() with default 'None' to handle blank fields gracefully
        text = (
            f"Program: {data.get('program', 'None')}\n"
            f"University: {data.get('university', 'None')}\n"
            f"Comments: {data.get('comments', 'None')}\n"
            f"Term: {data.get('term', 'None')}\n"
            f"Degree: {data.get('degree', 'None')}\n"
            f"Citizenship: {data.get('citizenship', 'None')}\n"
            f"GPA: {data.get('gpa', 'None')}\n"
            f"GRE Quant: {data.get('gre_q', 'None')}\n"
            f"GRE Verbal: {data.get('gre_v', 'None')}\n"
            f"GRE AW: {data.get('gre_aw', 'None')}"
        )

        # 2. Tokenize and Predict
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred_id = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_id].item()

        return ("Accepted" if pred_id == 1 else "Rejected"), round(confidence, 2)