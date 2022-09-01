<p align="center">
  <img src="https://user-images.githubusercontent.com/36517134/173432372-6757b6b5-7a9e-4832-a3d9-437f863e5fe2.png" alt="Sublime's custom image"/>
</p>

# Features

- Albums management
- Sharing
    - Different access levels
    - Sharing with other users or using a link
- Face Recognition
    - Detection of faces in photos
    - Naming of detected faces

# Demo
![image](https://user-images.githubusercontent.com/36517134/187902073-4daa897f-2275-408e-8163-f7b654e0522e.png)

# Technical details

- Written in `Python` using the `Django` framework.
- Designed with `HTML` and `SCSS`
- Running on `Heroku`
- `PostgreSQL` database hosted on `AWS`
- `AWS S3` for storing photos
- `Azure Cognitive Services` for face recognition

# Architecture

![image](https://user-images.githubusercontent.com/36517134/174063884-3ca70b73-b0c6-47ba-9c80-3946351d0f5a.png)

# Installation

FaceIt requires the following environment variables:

- `SECRET_KEY` - The Django secret key
- `EMAIL_USER` - The email address of the user used to send emails (gmail)
- `EMAIL_PASSWORD` - The password of the user used to send emails (gmail)
- `AWS_ACCESS_KEY_ID` - The access key id of the user used to store photos on AWS S3
- `AWS_SECRET_ACCESS_KEY` - The secret access key of the user used to store photos on AWS S3
- `AWS_BUCKET_NAME` - The name of the bucket used to store photos on AWS S3
- `AZURE_KEY` - The key of the user used to detect faces on Azure Cognitive Services
- `AZURE_ENDPOINT` - Azure Cognitive Services endpoint
- `DB_NAME` - The name of the database (postgres)
- `DB_USER` - The name of the user used to connect to the database
- `DB_PASSWORD` - The password of the user used to connect to the database
- `DB_HOST` - The host of the database
- `DB_PORT` - The port of the database

If you have everything set up, you can clone the repository and install the requirements:

`pip install -r requirements.txt`

Now you can run the application:

```
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8080
```

Make sure to run `python manage.py process_tasks` to enable face recognition and email valiation.
