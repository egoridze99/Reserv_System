from db import db

queue_room = db.Table('queue_room',
                      db.Column('queue_id', db.Integer, db.ForeignKey('reservation_queue.id', name="queue_id")),
                      db.Column('room_id', db.Integer, db.ForeignKey('room.id', name="room_id"))
                      )

reservation_transaction_dict = db.Table('reservation_transaction_dict', db.Column('reservation_id', db.Integer,
                                                                                  db.ForeignKey("reservation.id",
                                                                                                name="reservation_id")),
                                        db.Column('transaction_id', db.Integer,
                                                  db.ForeignKey("transaction.id", name="transaction_id"), unique=True))

certificate_transaction_dict = db.Table('certificate_transaction_dict', db.Column('certificate_id', db.Integer,
                                                                                  db.ForeignKey("certificate.id",
                                                                                                name="certificate_id")),
                                        db.Column('transaction_id', db.Integer,
                                                  db.ForeignKey("transaction.id", name="transaction_id"), unique=True))

cashier_transaction_dict = db.Table('cashier_transaction_dict',
                                    db.Column("cashier_id", db.Integer, db.ForeignKey("money.id", name="cashier_id")
                                              ), db.Column("transaction_id", db.Integer,
                                                           db.ForeignKey("transaction.id",
                                                                         name="transaction_id"), unique=True))

guest_comment_dict = db.Table('guest_comment_dict',
                              db.Column('comment_id', db.Integer, db.ForeignKey('guest_comment.id', name="comment_id"),
                                        unique=True),
                              db.Column('guest_id', db.Integer,
                                        db.ForeignKey('guest.id', name="guest_id"))
                              )

queue_logs = db.Table('queue_logs',
                      db.Column("log_id", db.Integer, db.ForeignKey('reservation_queue_view_log.id', name="log_id")),
                      db.Column('queue_id', db.Integer, db.ForeignKey('reservation_queue.id', name="queue_id"))
                      )
