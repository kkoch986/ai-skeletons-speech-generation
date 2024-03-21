FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /
RUN apt update
RUN apt install -y build-essential festival festival-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY inventory.csv inventory.csv
COPY inventory-full.csv inventory-full.csv
RUN python3 -m allosaurus.bin.download_model -m eng2102

RUN touch last.json
COPY main.py main.py 
COPY audio/ audio/
ENTRYPOINT python3 main.py api
