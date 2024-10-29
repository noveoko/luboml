import os
import gzip
import requests
import logging
import multiprocessing
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)

# Configuration variables
MAX_FILES = 10  # Set to None to process all WARC files
COMMON_CRAWL_BASE_URL = "https://data.commoncrawl.org/"

# Step 1: Data Collection - Parallel Processing for Common Crawl Data
def fetch_warc_urls():
    """Fetch WARC file URLs from Common Crawl index files."""
    cc_index_url = "https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2024-09/warc.paths.gz"
    response = requests.get(cc_index_url, stream=True)
    if response.status_code == 200:
        with gzip.open(response.raw, 'rt', encoding='utf-8') as f:
            for line in f:
                yield COMMON_CRAWL_BASE_URL + line.strip()
    else:
        logging.error("Failed to retrieve Common Crawl index file URLs.")

def download_and_parse_warc(warc_url):
    """Download and parse WARC file from Common Crawl, extracting text content."""
    logging.info(f"Processing WARC file: {warc_url}")
    documents = []
    response = requests.get(warc_url, stream=True)
    if response.status_code == 200:
        with gzip.open(response.raw, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    payload = record.content_stream().read().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(payload, 'html.parser')
                    text = soup.get_text()
                    documents.append(text)
    return documents

def parallel_process_warc_files(warc_urls, max_files=MAX_FILES):
    """Parallel processing of WARC files to extract text data."""
    documents = []
    with multiprocessing.Pool() as pool:
        results = pool.map(download_and_parse_warc, warc_urls[:max_files])
        for result in results:
            documents.extend(result)
    return documents

# Step 2: Feature Extraction
def feature_extraction(documents):
    """Extract TF-IDF features from documents."""
    vectorizer = TfidfVectorizer(max_features=1000)
    features = vectorizer.fit_transform(documents)
    return features, vectorizer

# Step 3: Model Training
def train_model(features, labels):
    """Train a machine learning model using SVM."""
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    model = SVC(kernel='linear')
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))
    
    # Save model and vectorizer for later use
    joblib.dump(model, 'common_crawl_classifier.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    return model

# Step 4: Classification
def classify_document(text, model, vectorizer):
    """Classify a new document based on the trained model."""
    features = vectorizer.transform([text])
    prediction = model.predict(features)
    return prediction

# Step 5: Main Execution and Control
if __name__ == "__main__":
    # Fetch and parse WARC URLs
    warc_urls = list(fetch_warc_urls())
    if not warc_urls:
        raise ValueError("No WARC URLs found. Check Common Crawl index URL.")
    
    # Process WARC files in parallel
    documents = parallel_process_warc_files(warc_urls, max_files=MAX_FILES)

    # Example Labels (for demonstration; replace with actual labels)
    labels = [1 if i % 2 == 0 else 0 for i in range(len(documents))]  # 1 = deep web, 0 = surface web

    # Feature Extraction
    features, vectorizer = feature_extraction(documents)

    # Train Model
    model = train_model(features, labels)

    # Classify new document example
    sample_text = "Sample content from a new document to classify."
    classification = classify_document(sample_text, model, vectorizer)
    print(f"Classification result: {classification}")
