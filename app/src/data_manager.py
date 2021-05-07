from .utils import time
from .utils.permanent_data import EVENT_TYPES, VARIABLES
from .utils.time import time_to_string
from .. import db
from ..models import Variable, Device, Experiment, Value, Event, EventType, Log


class DataManager:
    def __init__(self):
        self.last_seen_id = {'values': {}, 'events': {}}

        self.variables = self.load_variables()
        self.experiments = dict()

    def store_permanent(self):
        for item in EVENT_TYPES:
            self.insert(EventType(id=item[0], type=item[1]), EventType)
        for item in VARIABLES:
            self.insert(Variable(id=item[0], name=item[1], type=item[2]), Variable)

    @staticmethod
    def insert(item, item_class):
        from main import app
        with app.app_context():
            exists = item_class.query.filter_by(id=item.id).first()
            if not exists:
                db.session.add(item)
                db.session.commit()

    @staticmethod
    def update(item):
        from main import app
        with app.app_context():
            db.session.add(item)
            db.session.commit()

    @staticmethod
    def delete_log(log_id=None):
        from main import app
        with app.app_context():
            if log_id:
                Log.query.filter_by(id=log_id).delete()
            else:
                db.session.query(Log).delete()
                db.session.commit()

    def load_variables(self):
        return [var.id for var in Variable.query.all()]

    def save_value(self, value):
        if value.var_id not in self.variables:
            self.save_variable(value.var_id)
            self.variables.append(value.var_id)
        self.insert(value, Value)

    def save_variable(self, variable):
        variable = Variable(id=variable, type='measured')
        self.insert(variable, Variable)

    def save_event(self, event):
        self.insert(event, Event)

    def save_device(self, connector):
        device = Device(id=connector.device_id, device_class=connector.device_class,
                        device_type=connector.device_type, address=connector.address)
        self.insert(device, Device)

        # TEMPORAL HACK !!!
        self.save_experiment(device.id)

    # TEMPORAL HACK !!!
    def save_experiment(self, device_id, current_time=time.now()):
        experiment = Experiment(dev_id=device_id, start=current_time)
        self.insert(experiment, Experiment)
        self.experiments[device_id] = experiment

    # TEMPORAL HACK !!!
    def update_experiment(self, device_id):
        experiment = self.experiments.pop(device_id)
        experiment.end = time.now()
        self.update(experiment)

    def post_process(self, query_results, data_type, device_id):
        result = {}

        for obj in query_results:
            row = obj.__dict__
            log_id = row.pop('id')
            row['time'] = time_to_string(row['time'])
            if "_sa_instance_state" in row:
                del row['_sa_instance_state']
            result[log_id] = row

        if device_id is not None and len(result) != 0:
            self.last_seen_id[data_type][device_id] = max(list(map(int, result.keys())))

        return result

    def get_data(self, log_id: int, last_time: str, device_id: str, data_type: str = 'values'):
        cls = Value if data_type == 'values' else Event

        if last_time is not None:
            from main import app
            with app.app_context():
                return self.post_process(cls.query.filter_by(dev_id=device_id).filter(cls.time > last_time).all(),
                                         data_type, device_id)
        else:
            if log_id is None:
                log_id = self.last_seen_id[data_type].get(device_id, 0)
            from main import app
            with app.app_context():
                return self.post_process(cls.query.filter_by(dev_id=device_id).filter(cls.id > log_id).all(),
                                         data_type, device_id)

    def get_latest_data(self, device_id, data_type: str = 'values'):
        cls = Value if data_type == 'values' else Event

        from main import app
        with app.app_context():
            return cls.query.filter_by(dev_id=device_id).order_by(cls.id.desc()).first()

    def event_task_start(self, config):
        args = {'task_class': config['task_class'],
                'task_id': config['task_id'],
                'task_type': config['task_type']}
        event = Event(dev_id=config['device_id'], event_type=3, time=time.now(), args=str(args),
                      command='start task', response=str(True))
        self.save_event(event)

    def event_task_end(self, device_id, task_id):
        event = Event(dev_id=device_id, event_type=4, time=time.now(), args=str(task_id),
                      command='end task', response=str(True))
        self.save_event(event)

    def event_device_start(self, config):
        event = Event(dev_id=config['device_id'], event_type=3, time=time.now(), args=str(config),
                      command='start device', response=str(True))
        self.save_event(event)

    def event_device_end(self, device_id):
        event = Event(dev_id=device_id, event_type=4, time=time.now(), args=str(device_id),
                      command='end device', response=str(True))
        self.save_event(event)

    def store_log(self, init_type, config):
        value = Log(id=config[init_type + '_id'], type=init_type, config=config)
        self.insert(value, Log)

    def remove_log(self, id):
        self.delete_log(id)

    def remove_all_logs(self):
        self.delete_log()

    def load_log(self):
        with db.app.app_context():
            return Log.query.all()
