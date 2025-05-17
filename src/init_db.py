from flask import Flask
from config.db_config import Config, initialize_database

app = Flask(__name__)
app.config.from_object(Config)

if __name__ == '__main__':
    print("Initializing database...")
    initialize_database(app)
    print("Database initialized successfully!") 