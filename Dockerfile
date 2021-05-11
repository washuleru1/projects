FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt 

EXPOSE 8081

COPY . .
ENV SERVICE_ACCOUNT_IAM="./iam.json"
ENV TOPIC_ID="cloudsql-status"
ENV SERVICE_ACCOUNT_PUBSUB="./pubsub.json"
ENV TOPIC_PATH="projects/PROJECT-ID/topics/TOPIC-ID"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]

