import boto3
import gzip
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Step 1: Data Collection - Accessing Common Crawl Data
def fetch_common_crawl_data(index_url):
    """Download and extract data from Common Crawl WARC file."""
    logging.info(f"Fetching Common Crawl data from: {index_url}")
    response = requests.get(index_url, stream=True)
    if response.status_code == 200:
        # Open the WARC file in streaming mode
        with gzip.open(response.raw, 'rt', encoding='utf-8') as file:
            for line in file:
                if line.startswith('WARC-Target-URI'):
                    # Process only lines containing page URLs
                    url = line.strip().split(': ')[1]
                    logging.info(f"Processing URL: {url}")
                    yield url
    else:
        logging.error(f"Failed to fetch data from Common Crawl: {index_url}")

# Step 2: Preprocess Data
def extract_text_from_url(url):
    """Extracts and cleans text from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return ""

# Step 3: Feature Extraction
def feature_extraction(documents):
    """Extract TF-IDF features from text documents."""
    vectorizer = TfidfVectorizer(max_features=1000)
    features = vectorizer.fit_transform(documents)
    return features, vectorizer

# Step 4: Model Training
def train_model(features, labels):
    """Train a machine learning model using SVM."""
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    model = SVC(kernel='linear')
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))
    
    # Save model and vectorizer for future use
    joblib.dump(model, 'common_crawl_classifier.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    return model

# Step 5: Classify and Refine
def classify_document(text, model, vectorizer):
    """Classify a new text document based on the trained model."""
    features = vectorizer.transform([text])
    prediction = model.predict(features)
    return prediction

# Example Usage
if __name__ == "__main__":
    # Define the Common Crawl index and fetch URLs
    cc_index_url = "https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2024-09/wet.paths.gz"
    urls = fetch_common_crawl_data(cc_index_url)
    
    # Collect and process documents
    documents = []
    for url in urls:
        text = extract_text_from_url(url)
        if text:
            documents.append(text)
    
    # Create sample labels (for demonstration; replace with actual labels)
    labels = [1 if i % 2 == 0 else 0 for i in range(len(documents))]  # e.g., 1 = deep web, 0 = surface web
    
    # Feature Extraction
    features, vectorizer = feature_extraction(documents)
    
    # Train Model
    model = train_model(features, labels)
    
    # Classify a new document
    sample_text = "Sample content from a new document to classify."
    classification = classify_document(sample_text, model, vectorizer)
    print(f"Classification result: {classification}")
