FROM python:3.10-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the dashboard code
COPY dashboard.py .

# Expose the Streamlit port
EXPOSE 8501

# Run the dashboard and bind it to 0.0.0.0 so it can be accessed from outside the container
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0"]