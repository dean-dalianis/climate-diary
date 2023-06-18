FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY ./ /app

EXPOSE 3006

CMD ["python3", "main.py"]
