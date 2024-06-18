FROM python:3.9

WORKDIR /case_api

COPY ./requirements/generated/requirements.txt /case_api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /case_api/requirements.txt

COPY ./app /case_api/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]