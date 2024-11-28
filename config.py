import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'

    # SQLite database in the 'instance' folder
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(os.getcwd(), "instance", "site.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
