FROM kthse/kth-python:3.10.0

RUN mkdir /repo

WORKDIR /repo

# Install git
RUN apk upgrade && \
    apk update && \
    apk add --no-cache bash git openssh curl docker tzdata

RUN pip3 install pytz

ENV TZ=Europe/Stockholm
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Copy dependencies and install them
COPY ["Pipfile", "Pipfile"]
COPY ["Pipfile.lock", "Pipfile.lock"]
RUN pipenv install

# Copy the code
COPY ["log.py", "log.py"]
COPY ["run.py", "run.py"]
COPY ["modules", "modules"]

# Run the application through pipenv
CMD ["pipenv", "run", "python", "-u", "run.py"]
