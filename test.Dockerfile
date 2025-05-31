FROM imlappsregistry.azurecr.io/iml-df-base:v1

WORKDIR /code
COPY ./requirements-test.txt /code/requirements-test.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements-test.txt
COPY ./app /code/app

#CMD ["pytest", "/code/app/test_main.py", "--junitxml=test-results.xml"]