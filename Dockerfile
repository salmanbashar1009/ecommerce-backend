# use official python image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs appear immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies (optional but useful)
RUN apt-get update && apt-get install -y gcc

# copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY ' '

# expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD [ "uvicorn ","app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
