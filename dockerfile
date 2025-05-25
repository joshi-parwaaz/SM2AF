FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ignore all files in the uploads folder
RUN find . -path "uploads/*" -delete

# ignore all files in the .git folder
RUN find . -path ".git/*" -delete

# ignore all files in the .venv folder
RUN find . -path ".venv/*" -delete

# ignore all files in the __pycache__ folder
RUN find . -path "__pycache__/*" -delete


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]