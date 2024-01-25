"""Descripción de los cambios

Revision ID: 525207c241da
Revises: 
Create Date: 2024-01-22 19:53:49.638210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '525207c241da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Modificar la creación de tabla
# alembic upgrade head
#comando para aplicar el camnio
def upgrade() -> None:
    #op.add_column('actividades', sa.Column(
    #    'huevo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('actividades', 'id_lugar')


#para retroceder a la version anterior
# alembic downgrade -1
#cuidado que me parece que usa el de abajo, asi que siemmpre hacer el contrario
#por si acaso

def downgrade() -> None:
    # Revertir los cambios realizados en upgrade
    #op.drop_column('actividades', 'huevo')
    op.add_column('actividades', sa.Column(
        'id_lugar', sa.INTEGER(), autoincrement=False, nullable=True))
