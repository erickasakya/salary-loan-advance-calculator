FROM python:3.13-alpine
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]