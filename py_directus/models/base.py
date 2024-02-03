import re

from pydantic import ConfigDict
from pydantic._internal._config import ConfigWrapper
from pydantic.main import _model_construction, BaseModel


class DirectusConfigDict(ConfigDict):
    collection: str


class DirectusModelMetaclass(_model_construction.ModelMetaclass):
    """
    """

    def __new__(cls, name, bases, namespace, *args, **kwargs):
        """ Perform check for `collection` declaration """

        tmp_config_wrapper = ConfigWrapper.for_model((), namespace, kwargs)
        declared_collection = tmp_config_wrapper.config_dict.get("collection", None)

        completed_class = super().__new__(cls, name, bases, namespace, *args, **kwargs)

        class_config = getattr(completed_class, "model_config", None)

        if not declared_collection:
            output = re.findall("[A-Z]?[a-z]+", name)
            class_config["collection"] = "_".join([word.lower() for word in output])

        return completed_class


class DirectusModel(BaseModel, metaclass=DirectusModelMetaclass):
    pass
