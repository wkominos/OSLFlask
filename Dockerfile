FROM python:slim

RUN useradd accounts

WORKDIR /home/accounts

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY accounts.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP accounts.py

RUN chown -R accounts:accounts ./
USER accounts

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]