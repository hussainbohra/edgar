FROM jupyter/tensorflow-notebook

USER root

RUN apt-get update --fix-missing
RUN apt-get install -y swig
RUN apt-get install python-dev
RUN apt-get install curl
RUN apt-get install zip
RUN apt-get install unzip
RUN apt-get install -y libssl-dev
RUN apt-get install -y libcurl4-openssl-dev
RUN apt-get install -y python-dev

# create a symlink for development
RUN mkdir /development
RUN chmod 777 /development
RUN ln -s /development /home/jovyan/development

USER $NB_USER

#Amazon
RUN conda install -y boto3
RUN pip install awscli

# Python requirements
RUN pip install wget
RUN pip install html5lib
RUN pip install beautifulsoup4
RUN pip install pycurl
