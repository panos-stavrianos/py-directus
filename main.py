import json

from rich import print  # noqa

from py_directus import F

# age equals 23
F(age=23)

# age greater than 23
F(age__gt=23)

# age greater than and equal to 23
F(name__contains="John", age__gt=23)

### Combine filters

# age equals 23 and name equals John
F(age=23) & F(name="John")

# age equals 23 or name equals John
F(age=23) | F(name="John")

# age equals 23 and (name equals John or name equals Jane)
my_filter = F(age=23) & (F(name="John") | F(name="Jane"))

print(json.dumps(my_filter.query, indent=2))
