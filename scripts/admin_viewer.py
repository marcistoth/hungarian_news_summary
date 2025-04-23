import sys
import os

# allow importing from backend
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine # Use synchronous engine for Flask-Admin
from sqlalchemy.orm import scoped_session, sessionmaker

# Import settings and models from the backend
from backend.config import settings
from backend.models.db_models import ScrapedArticle, Summary
from backend.database import Base # Import Base to ensure models are registered

# Create Flask application
app = Flask(__name__)

db_filename = os.path.basename(settings.DATABASE_URL.split("///")[-1])
db_path = os.path.join(project_root, 'backend', db_filename)

sync_db_url = f"sqlite:///{db_path.replace(os.sep, '/')}"

engine = create_engine(sync_db_url)

# Create session factory bound to the synchronous engine
Session = scoped_session(sessionmaker(bind=engine))

admin = Admin(app, name='News Summary Admin', template_mode='bootstrap4') # Using bootstrap4

admin.add_view(ModelView(ScrapedArticle, Session))
admin.add_view(ModelView(Summary, Session))

if __name__ == '__main__':
    
    print(f"Admin interface running at http://127.0.0.1:5001/admin")
    print(f"Using database: {sync_db_url}")
    app.run(debug=True, port=5001) # Run on a different port than the FastAPI backend