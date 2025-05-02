import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from app.model import db, User

with app.app_context():
    db.create_all()
    print("Database initialized successfully.")
