from db import db

queue_room = db.Table('queue_room',
                      db.Column('queue_id', db.Integer, db.ForeignKey('reservation_queue.id', name="queue_id")),
                      db.Column('room_id', db.Integer, db.ForeignKey('room.id', name="room_id"))
                      )

checkout_reservation = db.Table('checkout_reservation',
                                db.Column('checkout_id', db.Integer, db.ForeignKey('checkout.id', name="checkout_id"),
                                          unique=True),
                                db.Column('reservation_id', db.Integer,
                                          db.ForeignKey('reservation.id', name="reservation_id"))
                                )

queue_logs = db.Table('queue_logs',
                      db.Column("log_id", db.Integer, db.ForeignKey('reservation_queue_view_log.id', name="log_id")),
                      db.Column('queue_id', db.Integer, db.ForeignKey('reservation_queue.id', name="queue_id"))
                      )
