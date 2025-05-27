from alembic import command
from alembic.config import Config
import os

def migrate():
    # Створюємо конфігурацію Alembic
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///instance/bank.db")
    
    # Застосовуємо міграцію
    command.upgrade(alembic_cfg, "head")

if __name__ == '__main__':
    migrate() 