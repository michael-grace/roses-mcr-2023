FROM python:3.9

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "./run.sh" ]