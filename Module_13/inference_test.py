import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def create_unified_input(data):
    """
    Ensures the input has all 10 lines in the correct order 
    so the model doesn't get confused.
    """
    return (f"Program: {data.get('program', 'None')}\n"
            f"University: {data.get('university', 'None')}\n"
            f"Comments: {data.get('comments', 'None')}\n"
            f"Term: {data.get('term', 'None')}\n"
            f"Degree: {data.get('degree', 'None')}\n"
            f"Citizenship: {data.get('citizenship', 'None')}\n"
            f"GPA: {data.get('gpa', 'None')}\n"
            f"GRE Quant: {data.get('gre_q', 'None')}\n"
            f"GRE Verbal: {data.get('gre_v', 'None')}\n"
            f"GRE AW: {data.get('gre_aw', 'None')}")

def run_test():
    model_path = "./admissions_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()
    
    # Define test cases as dictionaries (cleaner and safer)
    test_cases = [
        {
            "name": "Candidate A (Strong CS)",
            "data": {
                "program": "Computer Science",
                "university": "Stanford University",
                "comments": "3 years of research, 4.0 GPA, perfect GRE.",
                "term": "Fall 2026",
                "degree": "PhD",
                "citizenship": "American",
                "gpa": "4.0",
                "gre_q": "170.0",
                "gre_v": "165.0",
                "gre_aw": "5.0"
            }
        },
        {
            "name": "Candidate B (Weak History)",
            "data": {
                "program": "History",
                "university": "Local College",
                "comments": "No research, struggling with grades.",
                "term": "Fall 2026",
                "degree": "Master's",
                "citizenship": "American",
                "gpa": "2.1",
                "gre_q": "135.0",
                "gre_v": "140.0",
                "gre_aw": "2.0"
            }
        }
    ]
    
    softmax = torch.nn.Softmax(dim=1)
    
    print("--- SECTION 6: CORRECTED INFERENCE TEST ---")
    for case in test_cases:
        # 1. Format the string correctly using our function
        formatted_text = create_unified_input(case['data'])
        
        # 2. Tokenize
        inputs = tokenizer(formatted_text, return_tensors="pt", truncation=True, max_length=128, padding=True)
        
        # 3. Predict
        with torch.no_grad():
            outputs = model(**inputs)
            probs = softmax(outputs.logits)
            prediction = torch.argmax(probs, dim=1).item()
            conf = probs[0][prediction].item()
            
        status = "Accepted" if prediction == 1 else "Rejected"
        print(f"\nResult for {case['name']}:")
        print(f"  Prediction: {status}")
        print(f"  Confidence: {conf:.4f}")

if __name__ == "__main__":
    run_test()