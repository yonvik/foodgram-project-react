FROM python:3.8-slim

COPY /backend /app
COPY /data/ingredients.csv /data/ingredients.csv

WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
