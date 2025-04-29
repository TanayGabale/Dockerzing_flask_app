Dockerfile

1

#Use an official Python runtime as a parent image

2

FROM python:3.8-slim

3

4

#Set the working directory in the container

5

WORKDIR /app

6

7

#Copy the current directory contents into the container at /app

8

COPY. /app

9

18

#Install any needed dependencies specified in requirements.txt

11

RUN pip install-no-cache-dir -r requirements.txt

12

13

#Make port 5888 available to the world outside this container

14

15

EXPOSE 5000

16

#Define environment variable

17

ENV FLASK APP=app.py

18

19

#Run flask when the container launches

20

CMD ["flask", "run", "--host=0.0.0.0"]