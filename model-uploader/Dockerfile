FROM python:3.9

RUN python3 -m pip install kafka-python watchdog
COPY upload_models.py .

CMD python3 upload_models.py
