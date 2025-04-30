# ####### 👇 SIMPLE SOLUTION (x86 and M1) 👇 ########
FROM python:3.10.6-buster

WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libgl1

COPY utils/api.py api.py
COPY utils/app.py app.py
COPY best.pt best.pt

CMD uvicorn api:app --host 0.0.0.0 --port $PORT


# # Use Python 3.10-slim as a base image
# FROM python:3.10.6-buster


# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed dependencies specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 80 available to the world outside this container
# EXPOSE 8000

# # Define environment variables
# ENV API_URL="http://0.0.0.0:8000"

# # Run api.py when the container launches
# CMD ["uvicorn", "utils.api:app", "--host", "0.0.0.0", "--port", "8000"]
