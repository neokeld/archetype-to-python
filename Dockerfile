FROM python:3.10-slim

WORKDIR /usr/src/app

COPY ./src/ ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./archetype-parser.py" ]