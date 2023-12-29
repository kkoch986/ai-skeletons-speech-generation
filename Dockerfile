FROM pytorch/pytorch:latest

COPY requirements.txt requirements.txt
COPY main.py main.py 
COPY inventory.csv inventory.csv
COPY inventory-full.csv inventory-full.csv
RUN pip install -r requirements.txt

RUN python -m allosaurus.bin.download_model -m eng2102

ENTRYPOINT ./main.py api
