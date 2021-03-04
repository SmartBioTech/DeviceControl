from abc import ABCMeta
from copy import deepcopy


class DummyAttribute:
    pass


def abstractattribute(obj=None):
    if obj is None:
        obj = DummyAttribute()
    obj.__is_abstract_attribute__ = True
    return obj


class Interface(ABCMeta):

    def __call__(cls, *args, **kwargs):
        instance = ABCMeta.__call__(cls, *args, **kwargs)
        abstract_attributes = {
            name
            for name in dir(instance)
            if getattr(getattr(instance, name), '__is_abstract_attribute__', False)
        }
        if abstract_attributes:
            raise NotImplementedError(
                "Attributes missing: Can't instantiate abstract class {} with"
                " abstract attributes: {}".format(
                    cls.__name__,
                    ', '.join(abstract_attributes)
                )
            )

        return instance


class AbstractModel:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            a, b = deepcopy(self.__dict__), deepcopy(other.__dict__)
            # compare based on equality our attributes, ignoring SQLAlchemy internal stuff
            a.pop('_sa_instance_state', None)
            b.pop('_sa_instance_state', None)
            return a == b
        return False

    def __str__(self):
        attrs = deepcopy(self.__dict__)
        attrs.pop('_sa_instance_state', None)
        return "{} ({})".format(self.__class__, ", ".join(["{}: {}".format(item, attrs[item]) for item in attrs]))

    def __repr__(self):
        return str(self)
