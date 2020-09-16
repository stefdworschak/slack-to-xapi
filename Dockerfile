FROM ubuntu:20.04

RUN apt-get update && apt-get install curl wget vim -y
RUN apt-get install python3-pip -y

WORKDIR /app
COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY src/ /app/

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["/bin/bash"]