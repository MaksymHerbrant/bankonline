"""add recipient to transaction

Revision ID: add_recipient_to_transaction
Revises: 
Create Date: 2024-05-27 02:37:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_recipient_to_transaction'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Додаємо стовпець recipient_id
    op.add_column('transaction', sa.Column('recipient_id', sa.Integer(), nullable=True))
    # Додаємо зовнішній ключ
    op.create_foreign_key(
        'fk_transaction_recipient_id_user',
        'transaction', 'user',
        ['recipient_id'], ['id']
    )

def downgrade():
    # Видаляємо зовнішній ключ
    op.drop_constraint('fk_transaction_recipient_id_user', 'transaction', type_='foreignkey')
    # Видаляємо стовпець
    op.drop_column('transaction', 'recipient_id') 