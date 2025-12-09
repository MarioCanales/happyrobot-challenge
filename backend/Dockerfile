# backend/Dockerfile

FROM python:3.9-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy the 'app' folder and 'seed_loads.py' for populating the DB with mock data
COPY ./app /code/app
COPY ./seed_loads.py /code/seed_loads.py

# env file to be modified manually for this POC
RUN touch .env
# Seed the database with initial load data
RUN python seed_loads.py

EXPOSE 80
# Run app.main when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
