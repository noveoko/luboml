import joblib
from flask import Flask, request, jsonify

# Load the trained model and vectorizer
model = joblib.load('common_crawl_classifier.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def classify_document(text, model, vectorizer):
    """Classify a new document using the trained model."""
    # Transform the document using the loaded vectorizer
    features = vectorizer.transform([text])
    # Predict the class of the document
    prediction = model.predict(features)
    return prediction

# Example of classifying a single document
sample_text = "Sample text to classify."
classification = classify_document(sample_text, model, vectorizer)
print(f"Classification result: {classification}")

# Setup Flask web application
app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify_endpoint():
    """API endpoint to classify a document."""
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    prediction = classify_document(text, model, vectorizer)
    return jsonify({'classification': prediction[0]})

if __name__ == "__main__":
    # Run the Flask web server
    app.run(host='0.0.0.0', port=5000)
