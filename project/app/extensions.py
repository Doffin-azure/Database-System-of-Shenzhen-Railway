from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_principal import Principal, RoleNeed, Permission
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
principals = Principal()
login_manager = LoginManager()


# Define role-based permissions
admin_permission = Permission(RoleNeed('管理员'))
superuser_permission = Permission(RoleNeed('超级用户'))