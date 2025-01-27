import inspect
import json

from utils.helpers import convert_key_values_and_spaces


class HammerAppSettings:
    def to_dict(self):
        result = dict()
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith("__") and not inspect.ismethod(value):
                result[name] = value
        return result

    def to_json(self):
        converted_dict = convert_key_values_and_spaces(self.to_dict())
        return json.dumps(converted_dict)

    def to_query_string(self):
        return self.to_json().replace(" ", "")
