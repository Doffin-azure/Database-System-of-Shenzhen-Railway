import os

from flask import Flask,g
from config import Config
from .extensions import db, migrate
from app.main import bp as main_bp
from app.auth import bp as auth_bp
from .admin import bp as admin_bp  
from app.main.utils import build_station_graph

def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY before starting the application.")
    database_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not database_url:
        variable = "TEST_DATABASE_URL" if app.testing else "DATABASE_URL"
        raise RuntimeError(f"Set {variable} before connecting to the database.")
    if app.testing and database_url == os.environ.get("DATABASE_URL"):
        raise RuntimeError("Use a separate database for tests.")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    
   
    @app.before_request
    def initialize_graph():
        
        from .main.utils import build_station_graph
        g.station_graph,lines_stations  = build_station_graph()

    return app

    
