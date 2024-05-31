# Configuration for application

import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'j32u4g23j4123l4'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqldb://username:password@localhost/basename'
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/openapi.yaml'
