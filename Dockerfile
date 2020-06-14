FROM python:stretch

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]