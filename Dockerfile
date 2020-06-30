FROM python:3.7-alpine
RUN apk add --no-cache bash
RUN apk add --no-cache gcc g++ libffi libffi-dev musl-dev linux-headers git libxml2-dev libxslt-dev
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
RUN pytest