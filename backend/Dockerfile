# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NLTK_DATA=/app/nltk_data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data and sentence transformer model during build
RUN python -c "import nltk; \
    nltk.download('punkt', download_dir='/app/nltk_data'); \
    nltk.download('stopwords', download_dir='/app/nltk_data'); \
    nltk.download('wordnet', download_dir='/app/nltk_data'); \
    nltk.download('omw-1.4', download_dir='/app/nltk_data'); \
    nltk.download('averaged_perceptron_tagger', download_dir='/app/nltk_data'); \
    nltk.download('punkt_tab', download_dir='/app/nltk_data')"

# Pre-download sentence transformer model
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "run.py"]
