from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '${revision}'
down_revision = '${down_revision}'
branch_labels = ${branch_labels}
depends_on = ${depends_on}


def upgrade():
    ${upgrades}


def downgrade():
    ${downgrades}
