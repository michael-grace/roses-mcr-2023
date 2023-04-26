FROM python:3.9

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN echo "{}" > data.json

EXPOSE 5000

ENV TZ "Europe/London"

CMD [ "./run.sh" ]