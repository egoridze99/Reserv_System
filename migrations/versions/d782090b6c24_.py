"""Материализует служебные даты очереди (ReservationQueue) и индексы на queue_room

Revision ID: d782090b6c24
Revises: 11065661ad0e
Create Date: 2026-07-21 00:00:00.000000

"""
from datetime import datetime, timedelta

from alembic import op
import sqlalchemy as sa

from sqlite_functions.get_shift_date import get_shift_date


# revision identifiers, used by Alembic.
revision = 'd782090b6c24'
down_revision = '11065661ad0e'
branch_labels = None
depends_on = None


def _parse_datetime(value):
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _backfill(bind):
    rows = bind.execute(sa.text(
        "SELECT id, start_date, end_date, duration FROM reservation_queue"
    )).fetchall()

    for row in rows:
        # У элемента очереди может быть несколько залов в разных городах (queue_room).
        # Берём тот же выбор города, что и reduce_city_from_rooms в domains/queue/handlers/{post,put}.py
        # (последний зал с непустым городом по порядку join'а).
        city_rows = bind.execute(sa.text("""
            SELECT city.timezone FROM queue_room
            JOIN room ON queue_room.room_id = room.id
            JOIN cinema ON room.cinema_id = cinema.id
            JOIN city ON cinema.city_id = city.id
            WHERE queue_room.queue_id = :qid
        """), {"qid": row.id}).fetchall()

        timezone = None
        for city_row in city_rows:
            if city_row.timezone:
                timezone = city_row.timezone

        start_date = _parse_datetime(row.start_date)
        end_date = _parse_datetime(row.end_date)

        duration_end_date = start_date + timedelta(hours=row.duration)
        window_end_date = (end_date or start_date) + timedelta(hours=row.duration)
        shift_date = get_shift_date(start_date, timezone or "+00:00", row.duration)

        bind.execute(sa.text("""
            UPDATE reservation_queue
            SET duration_end_date = :duration_end_date,
                window_end_date = :window_end_date,
                shift_date = :shift_date
            WHERE id = :qid
        """), {
            "duration_end_date": duration_end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "window_end_date": window_end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "shift_date": shift_date.strftime("%Y-%m-%d"),
            "qid": row.id,
        })


def upgrade():
    bind = op.get_bind()

    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration_end_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('window_end_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('shift_date', sa.Date(), nullable=True))

    _backfill(bind)

    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.alter_column('duration_end_date', nullable=False)
        batch_op.alter_column('window_end_date', nullable=False)
        batch_op.alter_column('shift_date', nullable=False)
        batch_op.create_index(batch_op.f('ix_reservation_queue_duration_end_date'), ['duration_end_date'],
                              unique=False)
        batch_op.create_index(batch_op.f('ix_reservation_queue_window_end_date'), ['window_end_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_reservation_queue_shift_date'), ['shift_date'], unique=False)

    with op.batch_alter_table('queue_room', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_queue_room_queue_id'), ['queue_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_queue_room_room_id'), ['room_id'], unique=False)


def downgrade():
    with op.batch_alter_table('queue_room', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_queue_room_room_id'))
        batch_op.drop_index(batch_op.f('ix_queue_room_queue_id'))

    with op.batch_alter_table('reservation_queue', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reservation_queue_shift_date'))
        batch_op.drop_index(batch_op.f('ix_reservation_queue_window_end_date'))
        batch_op.drop_index(batch_op.f('ix_reservation_queue_duration_end_date'))
        batch_op.drop_column('shift_date')
        batch_op.drop_column('window_end_date')
        batch_op.drop_column('duration_end_date')
