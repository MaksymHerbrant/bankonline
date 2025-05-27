from app import create_app, db
from app.models import News

def init_news():
    app = create_app()
    with app.app_context():
        print("Файл ініціалізації новин")

if __name__ == '__main__':
    init_news() 