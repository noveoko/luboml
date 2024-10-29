import requests
import gzip
import logging
from retrying import retry

# Setup logging
logging.basicConfig(level=logging.INFO)

COMMON_CRAWL_INDEX_LIST_URL = "https://index.commoncrawl.org/collinfo.json"
COMMON_CRAWL_BASE_URL = "https://data.commoncrawl.org/"

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def fetch_latest_warc_index():
    """Retrieve the most recent Common Crawl index."""
    response = requests.get(COMMON_CRAWL_INDEX_LIST_URL)
    if response.status_code == 200:
        indexes = response.json()
        return indexes[0]['cdx-api'] + "/warc.paths.gz"
    else:
        logging.error("Failed to retrieve latest Common Crawl index.")
        return None

def fetch_warc_urls():
    """Fetch WARC file URLs from the latest Common Crawl index."""
    cc_index_url = fetch_latest_warc_index()
    response = requests.get(cc_index_url, stream=True)
    if response.status_code == 200:
        with gzip.open(response.raw, 'rt', encoding='utf-8') as f:
            for line in f:
                yield COMMON_CRAWL_BASE_URL + line.strip()
    else:
        logging.error("Failed to retrieve Common Crawl index file URLs.")

import multiprocessing
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import os

def download_and_parse_warc(warc_url):
    """Download and parse WARC file, extracting text."""
    logging.info(f"Processing WARC file: {warc_url}")
    documents = []
    try:
        response = requests.get(warc_url, stream=True)
        if response.status_code == 200:
            with gzip.open(response.raw, 'rb') as stream:
                for record in ArchiveIterator(stream):
                    if record.rec_type == 'response':
                        payload = record.content_stream().read().decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(payload, 'html.parser')
                        text = soup.get_text()
                        documents.append(text)
    except Exception as e:
        logging.error(f"Error processing WARC file {warc_url}: {e}")
    return documents

def parallel_process_warc_files(warc_urls, max_files=None):
    """Efficient parallel processing of WARC files."""
    documents = []
    num_files = len(warc_urls) if not max_files else min(len(warc_urls), max_files)
    pool_size = min(multiprocessing.cpu_count(), num_files)  # Dynamic pool size
    with multiprocessing.Pool(processes=pool_size) as pool:
        results = pool.map(download_and_parse_warc, warc_urls[:num_files])
        for result in results:
            documents.extend(result)
            # Optional: Save intermediate results to disk/database
    return documents

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

def feature_extraction(documents, num_features=1000, num_components=100):
    """Extract TF-IDF features and apply dimensionality reduction."""
    vectorizer = TfidfVectorizer(max_features=num_features)
    tfidf_matrix = vectorizer.fit_transform(documents)

    svd = TruncatedSVD(n_components=num_components, random_state=42)
    reduced_features = svd.fit_transform(tfidf_matrix)

    return reduced_features, vectorizer

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib

def train_model(features, labels):
    """Train an SVM model with hyperparameter optimization."""
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    
    # Define parameter grid
    param_grid = {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}
    
    # SVM with hyperparameter tuning
    grid_search = GridSearchCV(SVC(), param_grid, cv=3, n_jobs=-1, scoring='f1')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    predictions = best_model.predict(X_test)

    print(classification_report(y_test, predictions))
    logging.info(f"Best Parameters: {grid_search.best_params_}")

    # Save model and vectorizer for later use
    joblib.dump(best_model, 'common_crawl_classifier.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    return best_model

def classify_document(text, model, vectorizer):
    """Classify a new document."""
    features = vectorizer.transform([text])
    prediction = model.predict(features)
    return prediction

if __name__ == "__main__":
    # Fetch and parse WARC URLs
    warc_urls = list(fetch_warc_urls())
    if not warc_urls:
        raise ValueError("No WARC URLs found. Check Common Crawl index URL.")

    # Process WARC files in parallel
    documents = parallel_process_warc_files(warc_urls, max_files=MAX_FILES)

    # Example Labels should be replaced with actual data
    labels = [1 if i % 2 == 0 else 0 for i in range(len(documents))]  # Placeholder labels

    # Feature Extraction
    features, vectorizer = feature_extraction(documents)

    # Train Model
    model = train_model(featu
    sample_text = "Sample text to classify."
    classification = classify_document(sample_text, model, vectorizer)
    print(f"Classification result: {classification}")res, labels)

    # Classify a new document
