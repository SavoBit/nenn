FROM python:3.5-alpine
ARG FIXTURE=init

RUN apk update && apk add bind-tools  # nginx redis  # not yet

WORKDIR /usr/app/src
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
ADD . .
RUN python manage.py migrate && python manage.py loaddata $FIXTURE
# RUN head -c16 /dev/random | xxd -p > flag.txt  # not yet

ENV AWS_ACCESS_KEY_ID=AKIA01234567890ABCDE
ENV AWS_SECRET_ACCESS_KEY=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
