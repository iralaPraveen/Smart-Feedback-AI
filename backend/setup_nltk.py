import nltk

def setup_nltk_data():
    """Download required NLTK data"""
    resources = [
        'punkt',
        'stopwords', 
        'averaged_perceptron_tagger',
        'punkt_tab'
    ]
    
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
            print(f"✅ Downloaded {resource}")
        except Exception as e:
            print(f"❌ Failed to download {resource}: {e}")

if __name__ == "__main__":
    setup_nltk_data()
