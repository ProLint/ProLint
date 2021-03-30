# pull official base image
FROM continuumio/miniconda3

# set work directory
WORKDIR /usr/src/app

# we need gromacs sources for this. 
# we also need to fix all of these dependencies at some point
RUN mkdir /usr/src/gmx
ADD gsurf/source /usr/src/gmx
ENV GMX_MAXBACKUP -1
ENV PATH="/usr/src/app/gsurf:${PATH}"

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./environment.yml /usr/src/app/environment.yml
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "prolint", "/bin/bash", "-c"]

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/
RUN chmod +x /usr/src/app/gsurf/g_surf

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "prolint", "/bin/bash", "/usr/src/app/entrypoint.sh"]
