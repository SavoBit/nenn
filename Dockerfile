FROM python:3.5-alpine

WORKDIR /usr/app/src
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
ADD . .

USER nobody
ENV AWS_ACCESS_KEY_ID=AKIA01234567890ABCDE
ENV AWS_SECRET_ACCESS_KEY=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
