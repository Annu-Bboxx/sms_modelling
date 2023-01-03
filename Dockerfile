FROM python:3.9.12

RUN mkdir -p /app

COPY ./ /app/
COPY requirements.txt /requirements.txt
RUN cd /app

RUN pip install --upgrade pip
RUN cd /app \ && pip install -r requirements.txt

WORKDIR /app

CMD ["python3","./src/pipelines/predict_model.py"]