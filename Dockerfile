FROM python:3.10
ADD main.py .
COPY requirements.txt ./

RUN pip3 install mariadb==1.0.7
RUN pip install "fastapi[all]"
RUN pip install -r requirements.txt
EXPOSE 7200
COPY . .

CMD python -m uvicorn main:app  --reload --host 0.0.0.0 --port 7200

#Configure the mariaDB SQL connection to incule the username and passoword for remote connections.