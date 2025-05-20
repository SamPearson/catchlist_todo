#!/usr/bin/env python3
import os
from flask_migrate import Migrate
from src.config.models import db
from src.api.app_factory import create_app

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Create tables that don't exist yet
        db.create_all() 