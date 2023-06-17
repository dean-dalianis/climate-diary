FROM python:3.10-alpine

WORKDIR /diary_api

COPY requirements.txt /diary_api
RUN pip3 install -r requirements.txt

COPY ./ /diary_api

EXPOSE 3006

CMD ["python3", "app.py"]
