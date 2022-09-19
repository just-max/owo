FROM python:3.10

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /opt/owo/
WORKDIR /opt/owo/

RUN python -m pip install --no-cache-dir virtualenv \
    && python -m virtualenv ./

COPY requirements.txt ./
RUN source ./bin/activate \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir -r requirements.txt

RUN mkdir ./data/
VOLUME ./data
COPY ./owo.toml ./
COPY ./owo.toml ./data/

COPY ./main.py ./
COPY ./owobot/ ./owobot/

CMD source ./bin/activate \
    && python ./main.py ./data/owo.toml
