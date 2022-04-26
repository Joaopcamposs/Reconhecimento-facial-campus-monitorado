# pull official base image
FROM python:3.7

# set work directory
WORKDIR /Reconhecimento_facial

# copy requirements file
COPY requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# copy project
COPY . .

# expose the 3000 port from the localhost system
EXPOSE 8004

# run app
CMD ["uvicorn", "main:app", "--reload",  "--host", "0.0.0.0", "--port", "8000"]
