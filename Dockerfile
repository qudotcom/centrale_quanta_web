# 1. Base Image
FROM python:3.10-slim

# 2. Install Git
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 3. Install Dependencies First
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. --- THE REAL GAME FIX ---
# Clone the Google Unitary repository manually
RUN git clone https://github.com/quantumlib/unitary.git /app/google_quantum_lib

# Add the cloned folder to Python's search path so "import unitary" works
ENV PYTHONPATH="${PYTHONPATH}:/app/google_quantum_lib"

# 5. Copy your app code
COPY . .

# 6. Run
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
