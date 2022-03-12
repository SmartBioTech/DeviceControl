from .utils import time
from .utils.permanent_data import EVENT_TYPES, VARIABLES
from .utils.time import time_to_string
from .. import db
from ..models import Variable, Device, Experiment, Value, Event, EventType, Log


class DataManager:
    """
    Defines access points to the persistent data layer of the application.
    """
    def __init__(self):
        self.last_seen_id = {'values': {}, 'events': {}}

        self.variables = self.load_variables()
        self.experiments = dict()

    def _store_permanent(self):
        for item in EVENT_TYPES:
            self.insert(EventType(id=item[0], type=item[1]), EventType)
        for item in VARIABLES:
            self.insert(Variable(id=item[0], name=item[1], type=item[2]), Variable)

    @staticmethod
    def insert(item, item_class):
        """
        Executes an INSERT query and commits the change.

        :param item: Item to insert
        :param item_class: Class reference of the Item type
        """
        from main import app
        with app.app_context():
            exists = item_class.query.filter_by(id=item.id).first()
            if not exists:
                db.session.add(item)
                db.session.commit()

    @staticmethod
    def update(item):
        """
        Executes an UPDATE query and commits the change.

        :param item: Item to update
        """
        from main import app
        with app.app_context():
            db.session.add(item)
            db.session.commit()

    @staticmethod
    def delete_log(log_id=None):
        """
        Permanently deletes a log item. If no log_id is specified, ALL log items are deleted.

        :param log_id: ID of the log item
        """
        from main import app
        with app.app_context():
            if log_id:
                Log.query.filter_by(id=log_id).delete()
            else:
                db.session.query(Log).delete()
            db.session.commit()

    def load_variables(self):
        """
        Loads all variables from persistent storage.
        """
        return [var.id for var in Variable.query.all()]

    def save_value(self, value: Value):
        """
        Saves a Value object into persistent storage.

        :param value: value to save
        """
        if value.var_id not in self.variables:
            self.save_variable(value.var_id)
            self.variables.append(value.var_id)
        self.insert(value, Value)

    def save_variable(self, variable: Variable):
        """
        Saves a Variable object into persistent storage.

        :param variable: variable to save
        """
        variable = Variable(id=variable, type='measured')
        self.insert(variable, Variable)

    def save_event(self, event: Event):
        """
        Saves an Event object into persistent storage.

        :param event: event to save
        """
        self.insert(event, Event)

    def save_device(self, connector: Device):
        """
        Saves a Device object into persistent storage.

        :param connector: device to save
        """
        device = Device(id=connector.device_id, device_class=connector.device_class,
                        device_type=connector.device_type, address=connector.address)
        self.insert(device, Device)

        # TEMPORAL HACK !!!
        self.save_experiment(device.id)

    # TEMPORAL HACK !!!
    def save_experiment(self, device_id, current_time=time.now()):
        """
        Saves an Experiment object into persistent storage.

        :param device_id: device ID of the related Device
        :param current_time: time of the experiment, defaults to the current time.
        """
        experiment = Experiment(dev_id=device_id, start=current_time)
        self.insert(experiment, Experiment)
        self.experiments[device_id] = experiment

    # TEMPORAL HACK !!!
    def update_experiment(self, device_id):
        """
        Updates an Experiment object in persistent storage.

        :param device_id: device ID of the related Device
        """
        experiment = self.experiments.pop(device_id)
        experiment.end = time.now()
        self.update(experiment)

    def _post_process(self, query_results, data_type, device_id):
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

    def get_data(self, log_id: int, last_time: str, device_id: str, data_type: str = 'values') -> dict:
        """
        Retrieves data from persistent storage for a specified device. Further filters may be applied through
        additional parameters.

        :param log_id: ID of the log item to retrieve. Is ignored if the last_time parameter is not None.
        :param last_time: The timestamp in format <YYYYmmddHHMMSSfff>. Data from before this time will be excluded
                          from the response. If it's not None, the log_id parameter is ignored.
        :param device_id: device ID of the device
        :param data_type: defines the type of data to retrieve, defaults to 'values'
        :return: a dictionary with the data from persistent storage
        """
        cls = Value if data_type == 'values' else Event

        if last_time is not None:
            from main import app
            with app.app_context():
                return self._post_process(cls.query.filter_by(dev_id=device_id).filter(cls.time > last_time).all(),
                                          data_type, device_id)
        else:
            if log_id is None:
                log_id = self.last_seen_id[data_type].get(device_id, 0)
            from main import app
            with app.app_context():
                return self._post_process(cls.query.filter_by(dev_id=device_id).filter(cls.id > log_id).all(),
                                          data_type, device_id)

    def get_latest_data(self, device_id, data_type: str = 'values') -> dict:
        """
        Retrieves the data with the newest time for a specified device.

        :param device_id: device ID of the device
        :param data_type: defines the type of data to retrieve, defaults to 'values'
        :return: a dictionary with the data from persistent storage
        """
        cls = Value if data_type == 'values' else Event

        from main import app
        with app.app_context():
            return cls.query.filter_by(dev_id=device_id).order_by(cls.id.desc()).first()

    def event_task_start(self, config: dict):
        """
        Saves the information about a task start into persistent storage.

        Extra parameters:

        - 'task_id': string - ID of the task,
        - 'task_class': string - Class of the task,
        - 'task_type': Type of the task

        :param config: A dictionary with the specified extra parameters
        """
        args = {'task_class': config['task_class'],
                'task_id': config['task_id'],
                'task_type': config['task_type']}
        event = Event(dev_id=config['device_id'], event_type=3, time=time.now(), args=str(args),
                      command='start task', response=str(True))
        self.save_event(event)

    def event_task_end(self, device_id, task_id):
        """
        Saves the information about a task end into persistent storage.

        :param device_id: ID of the device to which the task corresponds
        :param task_id: ID of the task to end
        """
        event = Event(dev_id=device_id, event_type=4, time=time.now(), args=str(task_id),
                      command='end task', response=str(True))
        self.save_event(event)

    def event_device_start(self, config):
        """
        Saves the information about a device start into persistent storage.

        Extra parameters:

        - 'device_id': string - ID of the device,
        - 'device_class': string - Class of the device,
        - 'device_type': string - Type of the device,
        - 'address': string - Address on which the connection to the device can be established,

        :param config: A dictionary with the specified extra parameters
        """
        event = Event(dev_id=config['device_id'], event_type=3, time=time.now(), args=str(config),
                      command='start device', response=str(True))
        self.save_event(event)

    def event_device_end(self, device_id):
        """
        Saves the information about a device end into persistent storage.

        :param device_id: ID of the device to end
        """
        event = Event(dev_id=device_id, event_type=4, time=time.now(), args=str(device_id),
                      command='end device', response=str(True))
        self.save_event(event)

    def store_log(self, init_type, config):
        """
        Stores a log entry into persistent storage.

        :param init_type: type of the log entry
        :param config: config to log
        """
        value = Log(id=config[init_type + '_id'], type=init_type, config=config)
        self.insert(value, Log)

    def remove_log(self, id):
        """
        Removes a log entry from persistent storage.

        :param id: ID of the log entry to remove
        """
        self.delete_log(id)

    def remove_all_logs(self):
        """
        Removes all log entries.
        """
        self.delete_log()

    def load_log(self):
        """
        Retrieves all log entries.
        """
        with db.app.app_context():
            return Log.query.all()
