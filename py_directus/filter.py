import json

from rich import print  # noqa
from rich.console import Console  # noqa

from py_directus.expression import Expression
from py_directus.operators import FILTER_OPERATORS


class F(Expression):
    """
    Filter field.
    """

    def __init__(self, **kwargs):
        # Initialize the query as an empty dictionary
        self.query = {}

        # Parse keyword arguments into query format
        for key, value in kwargs.items():
            field, operator = F.parse_key(key)
            if not field:  # its a logical operator
                self.query[operator] = value
                continue
            field_parts = field.split(".")
            field = field_parts[0]

            if field not in self.query:
                self.query[field] = {}
            # convert deep fields from dot notation to nested dicts
            if len(field_parts) > 1:
                inner_dict = {operator: value}
                for part in reversed(field_parts[1:]):
                    inner_dict = {part: inner_dict}
                self.query[field] = {**self.query[field], **inner_dict}
            else:
                self.query[field][operator] = value

        if len(kwargs.items()) > 1:
            inner_queries = []
            for key, value in kwargs.items():
                inner_queries.append(F(**{key: value}).query)
            self.query = {"_and": inner_queries}

    @staticmethod
    def parse_key(key):
        field = None
        operator = None

        for _operator in FILTER_OPERATORS:
            if key.endswith("_" + _operator):
                field = key[:-len("_" + _operator)]
                operator = _operator
                break

        # No operator matched, which we assume was not provided.
        # Thus we use the default 'equals' operator.
        if field is None:
            operator = "_eq"
            field = key.replace("__", ".")
            return field, operator

        # Deep fields
        field = field.replace("__", ".")

        if field == "":
            field = None
        return field, operator

    def combine(self, other: 'F', operator: str) -> 'F':
        if other is None:
            return self
        else:
            if other.query == {}:
                return self
            elif self.query == {}:
                return other
            return F(**{operator: [self.query, other.query]})

    def __and__(self, other: 'F'):
        return self.combine(other, "__and")

    def __or__(self, other: 'F'):
        return self.combine(other, "__or")

    def __rand__(self, other: 'F'):
        return self.__and__(other)

    def __ror__(self, other: 'F'):
        return self.__or__(other)

    def __str__(self):
        return f"\n{json.dumps(self.query, indent=2)}\n"

    def __json__(self):
        return json.dumps(self.query, indent=2)

    def convert_query_to_string(self, input_dict):
        if "_or" in input_dict or "_and" in input_dict:
            key = "_or" if "_or" in input_dict else "_and"
            op_list = input_dict[key]
            return "(" + f"{FILTER_OPERATORS[key]}".join(
                [self.convert_query_to_string(subdict) for subdict in op_list]) + ")"
        else:
            key, value = list(input_dict.items())[0]
            if isinstance(value, dict):
                inner_str = " ".join([f"{FILTER_OPERATORS[k]} {v}" for k, v in value.items()])

                return f"({key} {inner_str})"

    def get_explanation(self, tab_char="  "):
        input_ex = self.convert_query_to_string(self.query)
        tabs = 0
        index = 0
        min_tabs = 500
        result = ""

        while True:
            if input_ex[index] == '(':
                tabs += 1
                result += '\n' + tab_char * tabs + input_ex[index]
            elif input_ex[index] == ')':
                tabs -= 1
                result += '\n' + tab_char * tabs + input_ex[index]
            else:
                min_tabs = min(min_tabs, tabs)
                result += input_ex[index]
            index += 1
            if index == len(input_ex):
                break

        result = result.replace('(', '').replace(')', '')
        result = result.split('\n')
        result = filter(lambda x: x.strip(tab_char) != '', result)
        result = list(map(lambda x: x[min_tabs * len(tab_char):], result))

        return "\n".join(result)

    def print_explanation(self, tab_char="  "):
        console = Console()
        explain = self.get_explanation(tab_char)

        for i in explain.split('\n'):
            if "AND" in i or "OR" in i:
                console.print(i, style="bold")
                continue
            count_tabs = i.count(tab_char)
            console.print(i, style=f"color({count_tabs})", highlight=False)
