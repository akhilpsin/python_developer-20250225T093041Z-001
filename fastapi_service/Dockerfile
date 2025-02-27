# lightweight Python image
FROM python:3.9.16-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Runing the tests (optional)
RUN pytest --tb=short --disable-warnings || true

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]