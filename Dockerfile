FROM python:3.10
WORKDIR /autoFilesSystem

RUN pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

ENV TIMEOUT=15

CMD python ./server.py $TIMEOUT
