FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY run.py .

# Create directories for data and logs
RUN mkdir -p data logs

# Expose the port the app runs on
EXPOSE 7450

# Set the command to run the application
CMD ["python", "run.py"]