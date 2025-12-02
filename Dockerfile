# 1. Use an official lightweight Python image
FROM python:3.10-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Install git (Required for installing Google's 'unitary' library from GitHub)
# We also clean up the apt cache afterwards to keep the image size small.
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements file first (This leverages Docker caching for faster builds)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
