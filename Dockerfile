# VERSION 1.10.10
# AUTHOR: Binh Phan
# DESCRIPTION: greenr-airflow container
# BUILD: docker build --rm -t btphan95/greenr-airflow .
# SOURCE: https://github.com/btphan95/greenr-airflow

FROM python:3.9.12

LABEL maintainer="Binh_"

#ENV DEBIAN_FRONTEND noninteractive
#ENV TERM linux

# Airflow variables
ARG AIRFLOW_VERSION=1.10.10
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

# Define en_US
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8



COPY configs/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg
COPY requirements.txt requirements.txt
#RUN pip install git+https://github.com/fastai/fastai.git

RUN apt-get upgrade
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY dags ${AIRFLOW_USER_HOME}/dags

COPY scripts ${AIRFLOW_USER_HOME}/scripts
# Install required libraries
EXPOSE 8008 8080
#USER airflow
#RUN chown -R airflow:airflow ${AIRFLOW_USER_HOME}
WORKDIR ${AIRFLOW_USER_HOME}
COPY scripts/entrypoint.sh /entrypoint.sh
#RUN chmod +x entrypoint.sh scripts/entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]