from flask import Flask
from config.db_config import Config, initialize_database

app = Flask(__name__)
app.config.from_object(Config)

if __name__ == '__main__':
    initialize_database(app) 