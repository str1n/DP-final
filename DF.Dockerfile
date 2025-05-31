FROM imlappsregistry.azurecr.io/iml-df-base:v1

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]