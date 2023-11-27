import re
import inspect

from pydantic.main import _model_construction, BaseModel


class DirectusModelMetaclass(_model_construction.ModelMetaclass):
    def __init__(cls, name, bases, dct, *args, **kwargs):
        # Perform check for `collection` declaration
        config_class = dct.get("Config", None)

        if inspect.isclass(config_class):
            if not hasattr(config_class, "collection"):
                output = re.findall("[A-Z]?[a-z]+", name)
                config_class.collection = "_".join([word.lower() for word in output])

        super().__init__(name, bases, dct, *args, **kwargs)


class DirectusModel(BaseModel, metaclass=DirectusModelMetaclass):
    pass
