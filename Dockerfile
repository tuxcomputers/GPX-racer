FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY gpx_racer /app/gpx_racer
COPY app.py /app/app.py
COPY pages /app/pages

RUN pip install --no-cache-dir .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
