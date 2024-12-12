from flask import Flask
from flask_migrate import Migrate
from extensions import db, bcrypt, login_manager
from models import User
from routes import main_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)


    Migrate(app, db)

    # Register the main blueprint
    app.register_blueprint(main_routes)

    # Setup login manager to redirect to login page when not authenticated
    login_manager.login_view = 'main_routes.login'

    # Set-up the user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

# Initialize the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
