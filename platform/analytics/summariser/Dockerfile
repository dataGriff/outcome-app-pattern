FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV SUMMARISE_INTERVAL_SECONDS=15

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY summarise_daily.py ./

CMD ["python", "summarise_daily.py"]
