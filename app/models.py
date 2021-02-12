from . import db
import enum
from sqlalchemy.dialects.mysql import DATETIME


class VariableType(enum.Enum):
    MEASURED = 'measured'
    COMPUTED = 'computed'
    ADJUSTED = 'adjusted'
    AGGREGATED = 'aggregate'


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.String(100), primary_key=True)
    device_class = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=True, default=None)


class Value(db.Model):
    __tablename__ = 'values'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(DATETIME(fsp=3), nullable=False)
    value = db.Column(db.Float, nullable=False)
    dev_id = db.Column(db.String(100), db.ForeignKey('devices.id'), nullable=False)
    var_id = db.Column(db.String(100), db.ForeignKey('variables.id'), nullable=False)
    attribute = db.Column(db.Integer, nullable=True, default=None)
    note = db.Column(db.String(100), nullable=True, default=None)


class Variable(db.Model):
    __tablename__ = 'variables'
    id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(VariableType), nullable=True, default=None)
    unit = db.Column(db.String(30), nullable=True, default=None)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.String(100), db.ForeignKey('devices.id'), nullable=False)
    event_type = db.Column(db.Integer, db.ForeignKey('event_types.id'), nullable=False)
    time = db.Column(DATETIME(fsp=3), nullable=False)
    args = db.Column(db.String(100), nullable=False)
    command = db.Column(db.String(100), nullable=False)
    response = db.Column(db.String(100), nullable=False)


class EventType(db.Model):
    __tablename__ = 'event_types'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)


# TEMPORAL HACK !!!
class Experiment(db.Model):
    __tablename__ = 'experiments'
    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.String(100), db.ForeignKey('devices.id'), nullable=False)
    start = db.Column(DATETIME(fsp=3), nullable=False)
    end = db.Column(DATETIME(fsp=3), nullable=True, default=None)
    description = db.Column(db.String(100), nullable=True, default=None)
