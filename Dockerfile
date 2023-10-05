FROM docker.io/pandoc/latex
WORKDIR /src

# https://stackoverflow.com/questions/68673221/warning-running-pip-as-the-root-user
ENV PIP_ROOT_USER_ACTION=ignore 

# Install Python dependencies (including pypandoc)
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install lxml
RUN pip3 install pypandoc

COPY convert.py .
ENTRYPOINT ["python", "convert.py"]
#CMD ["--filename=mediawiki_dump.xml", "--output=/src/output"]

