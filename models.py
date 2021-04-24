from datetime import datetime, timedelta

from app import db
import enum


class ReservStatusEnum(enum.Enum):
    not_allowed = "not_allowed"
    progress = 'progress'
    waiting = 'waiting'
    finished = 'finished'
    canceled = 'canceled'

class EmployeeRoleEnum(enum.Enum):
    root = "root"
    admin = "admin"
    operator = "operator"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    reservation = db.relationship("Reservation", backref='room')

    def __str__(self):
        return "<Зал id = {} название = {}>".format(self.id, self.name)


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    telephone = db.Column(db.String(30), nullable=False)
    reservation = db.relationship("Reservation", backref='guest')

    def __str__(self):
        return "<Гость id = {} Имя = {} Номер = {}>".format(self.id, self.name, self.telephone)


checkout_reservaion = db.Table('checkout_reservaion',
    db.Column('checkout_id', db.Integer, db.ForeignKey('checkout.id'), unique=True),
    db.Column('reservation_id', db.Integer, db.ForeignKey('reservation.id'))
)


class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    summ = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    reservation = db.relationship('Reservation', secondary=checkout_reservaion)


class Money(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    income = db.Column(db.Integer, nullable=False, default=0)
    expense = db.Column(db.Integer, nullable=False, default=0)
    proceeds = db.Column(db.Integer, nullable=False, default=0)
    cashier_start = db.Column(db.Integer, nullable=False, default=0)
    cashier_end = db.Column(db.Integer, nullable=False, default=0)
    all_by_card = db.Column(db.Integer, nullable=False, default=0)
    all_by_cash = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'date' in kwargs:
            date = kwargs['date']
            previous_day = date - timedelta(days=1)

            while True:
                previous_day_money_object = Money.query.filter(Money.date == str(previous_day)).first()

                if previous_day_money_object is not None:
                    self.cashier_start = previous_day_money_object.cashier_end
                    return

                previous_day -= timedelta(days=1)

    def __str__(self):
        return f"""
        <Деньги date={self.date} 
        income={self.income} 
        expense = {self.expense}
        proceeds = {self.proceeds}
        cashier_start = {self.cashier_start}
        cashier_end = {self.cashier_end}
        all_by_card = {self.all_by_card}
        all_by_cash = {self.all_by_cash}>
        """


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer)  # Кол-во гостей
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    film = db.Column(db.String(170))
    note = db.Column(db.Text)
    author = db.Column(db.String(120))
    checkout = db.relationship('Checkout', secondary=checkout_reservaion)

    status = db.Column(db.Enum(ReservStatusEnum), default=ReservStatusEnum.not_allowed, nullable=False)

    sum_rent = db.Column(db.Integer, default=0)
    card = db.Column(db.Integer, default=0)
    cash = db.Column(db.Integer, default=0)

    def __str__(self):
        return """
            <
            id = {}
            Резерв дата = {}  время = {}  продолжительность = {}
            количество гостей = {} 
            зал = {} 
            гость = {}
            фильм = {} 
            статус = {}
            по карте = {} 
            наличка = {}
            >
        """.format(self.id, self.date, self.time, self.duration, self.count, self.room, self.guest,
                   self.film, self.status, self.card,
                   self.cash)


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(EmployeeRoleEnum), default=EmployeeRoleEnum.admin)
    name = db.Column(db.String(40))
    surname = db.Column(db.String(40))