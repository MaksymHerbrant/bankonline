from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates')),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../static')))
    app.config.from_object(Config)
    
    # Налаштування сесії
    app.config['SESSION_COOKIE_SECURE'] = False  # Для локальної розробки
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 хвилин
    app.secret_key = Config.SECRET_KEY
    
    print("Ініціалізація додатку...")
    
    # Ініціалізація SQLAlchemy
    db.init_app(app)
    print("SQLAlchemy ініціалізовано")
    
    # Ініціалізація Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.index'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'basic'  # Змінюємо на 'basic' для тестування
    print("Flask-Login ініціалізовано")
    
    # Ініціалізація Flask-Bcrypt
    bcrypt.init_app(app)
    print("Flask-Bcrypt ініціалізовано")
    
    # Імпорт Blueprint після ініціалізації додатку
    with app.app_context():
        from app.routes import main_bp
        app.register_blueprint(main_bp)
        print("Blueprint зареєстровано")
        
        db.create_all()
        print("База даних ініціалізована")

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    try:
        user = User.query.get(int(user_id))
        print(f"Завантаження користувача: {user_id} -> {user}")
        return user
    except Exception as e:
        print(f"Помилка при завантаженні користувача: {str(e)}")
        return None