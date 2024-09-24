# Use a non-slim base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the port the Django app runs on
EXPOSE 8000

# Command to run when starting the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]







