ARG BASE_IMAGE=python:3.12-slim
FROM $BASE_IMAGE AS base

ARG REQUIREMENTS=requirements-production.txt

# Create a non-root user
RUN adduser --disabled-password app -u 1000 && \
    cp /usr/share/zoneinfo/Europe/London /etc/localtime

RUN mkdir /home/app/case_api
WORKDIR /home/app/case_api

COPY requirements/generated/$REQUIREMENTS requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app ./app

COPY alembic.ini ./alembic.ini

# Change ownership of the working directory to the non-root user
RUN chown -R app:app /home/app

# Cleanup container
RUN rm -rf /var/lib/apt/lists/*

# Switch to the non-root user
USER app

# Expose the Flask port
EXPOSE 8026

#CMD ["cat",  "app/__init__.py"]
CMD ["uvicorn", "app.__init__:case_api", "--port",  "8026", "--host", "0.0.0.0"]
