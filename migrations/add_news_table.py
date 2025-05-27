from app import db
from app.models import News

def upgrade():
    db.create_all()

def downgrade():
    db.drop_all() 