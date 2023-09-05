import json

from rich import print  # noqa
from rich.console import Console  # noqa

operators = {
    "_eq": "Equals",
    "_neq": "Doesn't equal",
    "_lt": "Less than",
    "_lte": "Less than or equal to",
    "_gt": "Greater than",
    "_gte": "Greater than or equal to",
    "_in": "Is one of",
    "_nin": "Is not one of",
    "_null": "Is null",
    "_nnull": "Isn't null",
    "_contains": "Contains",
    "_icontains": "Contains case-insensitive",
    "_ncontains": "Doesn't contain",
    "_starts_with": "Starts with",
    "_istarts_with": "Starts with case-insensitive",
    "_nstarts_with": "Doesn't start with",
    "_nistarts_with": "Doesn't start with case-insensitive",
    "_ends_with": "Ends with",
    "_iends_with": "Ends with case-insensitive",
    "_nends_with": "Doesn't end with",
    "_niends_with": "Doesn't end with case-insensitive",
    "_between": "Is between",
    "_nbetween": "Isn't between",
    "_empty": "Is empty",
    "_nempty": "Isn't empty",
    "_intersects": "Intersects",
    "_nintersects": "Doesn't intersect",
    "_intersects_bbox": "Intersects Bounding box",
    "_nintersects_bbox": "Doesn't intersect bounding box",
    "_and": "AND",
    "_or": "OR",
}


class F:

    def __init__(self, **kwargs):

        # Initialize the query as an empty dictionary
        self.query = {}
        # Parse keyword arguments into query format
        for key, value in kwargs.items():
            field, operator = F.parse_key(key)
            if not field:  # its a logical operator
                self.query[operator] = value
                continue
            if field not in self.query:
                self.query[field] = {}
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
        for _operator in operators:
            if key.endswith("_" + _operator):
                field = key[:-len("_" + _operator)]
                operator = _operator
                break
        if field is None:
            operator = "_eq"
            field = key.replace("__", ".")
            return field, operator

        field = field.replace("__", ".")

        if field == "":
            field = None
        return field, operator

    def __and__(self, other: 'F'):
        # Implement the logical AND operator
        return F(__and=[self.query, other.query])

    def __or__(self, other: 'F'):
        # Implement the logical OR operator
        return F(__or=[self.query, other.query])

    def __str__(self):
        return f"\n{json.dumps(self.query, indent=2)}\n"

    def convert_query_to_string(self, input_dict):
        if "_or" in input_dict or "_and" in input_dict:
            key = "_or" if "_or" in input_dict else "_and"
            op_list = input_dict[key]
            return "(" + f"{operators[key]}".join([self.convert_query_to_string(subdict) for subdict in op_list]) + ")"
        else:
            key, value = list(input_dict.items())[0]
            if isinstance(value, dict):
                inner_str = " ".join([f"{operators[k]} {v}" for k, v in value.items()])

                return f"({key} {inner_str})"

    def get_explanation(self, tab_char='  '):
        input_ex = self.convert_query_to_string(self.query)
        tabs = 0
        index = 0
        min_tabs = 500
        result = ''
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

    def print_explanation(self, tab_char='  '):
        console = Console()
        explain = self.get_explanation(tab_char)
        for i in explain.split('\n'):
            if "AND" in i or "OR" in i:
                console.print(i, style="bold")
                continue
            count_tabs = i.count(tab_char)
            console.print(i, style=f"color({count_tabs})", highlight=False)


if __name__ == '__main__':
    q1 = F(pools__name__eq="panos", hair__eq="brown")
    q2 = F(age__starts_with=23)
    q3 = F(job='programmer')

    combined_query = q1 | q3 | q3 | q2

    combined_query.print_explanation()
