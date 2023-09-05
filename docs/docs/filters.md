# Filters

## Simple Filters

``` python
from py_directus import F

# age equals 23
F(age=23)

# age greater than 23
F(age__gt=23)

# age greater than and equal to 23
F(name__contains="John", age__gt=23)
```

## Combine filters

``` python
# age equals 23 and name equals John
F(age=23) & F(name="John")

# age equals 23 or name equals John
F(age=23) | F(name="John")

# age equals 23 and (name equals John or name equals Jane)
F(age=23) & (F(name="John") | F(name="Jane"))
```

## Syntax

### Filter Operators

As you can see in the examples above, to use a filter you need to create an instance of the `F` class. The `F` class
takes keyword arguments, where the key is the field name and operator, and the value is the filter value.

!!! info ""
    If you don't specify an operator, the `__eq` operator will be used.


See the full list of operators [here](#full-list-of-operators).
 
### Logical Operators

The allowed logical operators are `&` (and) and `|` (or). You can **NOT** use `~` (not) to negate a filter as it is not
supported by directus.

Multiple values for the same filter will be combined with the `AND` operator.

``` python
# age greater than and equal to 23
F(name__contains="John", age__gt=23)
```

In order to combine multiple filters and nest them, you can use the logical operators.

``` python
# age equals 23 and (name equals John or name equals Jane)
F(age=23) & (F(name="John") | F(name="Jane"))
```

## Debugging your filters

In order to debug a filter, you can use the `get_explanation` method.

``` python
from py_directus import F
# age equals 23 and (name equals John or name equals Jane)
my_filter = F(age=23) & (F(name="John") | F(name="Jane"))
print(my_filter.get_explanation(tab_char='| '))
```

The output will be a string that you can use to debug your filter.

``` text
| age Equals 23
AND
| | name Equals John
| OR
| | name Equals Jane
```

Also, you can use the `print_explanation` method to get the explanation using the `rich` library with nice colors!

``` python
my_filter.print_explanation(tab_char='| ')
```

### Raw output

If you want to get the json output of the filter, you can use the `query` property.

``` python
print(my_filter.query)
```

The output will be a dictionary that you can use to debug your filter.

``` json
{
  "_and": [
    {
      "age": {
        "_eq": 23
      }
    },
    {
      "_or": [
        {
          "name": {
            "_eq": "John"
          }
        },
        {
          "name": {
            "_eq": "Jane"
          }
        }
      ]
    }
  ]
}
```

## Full list of operators

| Operator             | Description                         |
|----------------------|-------------------------------------|
| `__eq`               | Equals                              |
| `__neq`              | Doesn't equal                       |
| `__lt`               | Less than                           |
| `__lte`              | Less than or equal to               |
| `__gt`               | Greater than                        |
| `__gte`              | Greater than or equal to            |
| `__in`               | Is one of                           |
| `__nin`              | Is not one of                       |
| `__null`             | Is null                             |
| `__nnull`            | Isn't null                          |
| `__contains`         | Contains                            |
| `__icontains`        | Contains case-insensitive           |
| `__ncontains`        | Doesn't contain                     |
| `__starts_with`      | Starts with                         |
| `__istarts_with`     | Starts with case-insensitive        |
| `__nstarts_with`     | Doesn't start with                  |
| `__nistarts_with`    | Doesn't start with case-insensitive |
| `__ends_with`        | Ends with                           |
| `__iends_with`       | Ends with case-insensitive          |
| `__nends_with`       | Doesn't end with                    |
| `__niends_with`      | Doesn't end with case-insensitive   |
| `__between`          | Is between                          |
| `__nbetween`         | Isn't between                       |
| `__empty`            | Is empty                            |
| `__nempty`           | Isn't empty                         |
| `__intersects`       | Intersects                          |
| `__nintersects`      | Doesn't intersect                   |
| `__intersects_bbox`  | Intersects Bounding box             |
| `__nintersects_bbox` | Doesn't intersect bounding box      |


 