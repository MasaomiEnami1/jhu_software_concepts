from flask import Flask, render_template, request
from inference import AdmissionsPredictor

app = Flask(__name__)
predictor = AdmissionsPredictor()

@app.route('/will-you-get-in', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # 1. Collect form values
            # Safeguard: Validate numeric input gracefully
            gpa = request.form.get('gpa', '0.0')
            gre_q = request.form.get('gre_q', '0.0')
            
            user_data = {
                'program': request.form.get('program'),
                'university': request.form.get('university'),
                'comments': request.form.get('comments', ''), # Empty string if blank
                'term': request.form.get('term'),
                'degree': request.form.get('degree'),
                'citizenship': request.form.get('citizenship'),
                'gpa': gpa,
                'gre_q': gre_q,
                'gre_v': request.form.get('gre_v', '0.0'),
                'gre_aw': request.form.get('gre_aw', '0.0')
            }
            
            # 2. Run Inference
            result, score = predictor.predict(user_data)
            
            # 3. Display Result
            return render_template('result.html', prediction=result, confidence=score)
        
        except Exception as e:
            # Prevent raw stack traces on the webpage
            return f"An error occurred: {str(e)}. Please check your numeric inputs."

    return render_template('predict.html')

if __name__ == '__main__':
    app.run(debug=True)