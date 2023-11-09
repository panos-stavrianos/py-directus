# Aggregators

```python
Agg("*__count")

# OR

Agg(count="*")

# OR

Agg(operator=AggregationOperators.Count, fields="*")
```

Aggregate the number of records in the query

```python
await directus.collection("directus_users").aggregate().read()

# OR

await directus.collection("directus_users").aggregate(count="*").read()
```

To add multiple aggregates you can chain the `aggregate` method

```python
await directus.collection("products")
.aggregate(countDistinct="id")
.aggregate(sum="price").read()
```

## Agg object

### Usage

You can aggregate the data by defining the needed aggregation with the `Agg` class and passing it to the `aggregate` method

```python
from py_directus.aggregator import Agg

agg_obj = Agg()  # defaults to count='*'

await directus.collection("directus_users").aggregate(agg_obj).read()
```

In case you need only certain fields

```python
from py_directus.aggregator import Agg
from py_directus.operators import AggregationOperators

amount_agg = Agg(operator=AggregationOperators.Sum, fields="amount")

await directus.collection("transactions").aggregate(amount_agg).read()
```

### Complex Aggregation

```python
from py_directus.aggregator import Agg
from py_directus.operators import AggregationOperators

complex_aggregate = (
    Agg(operator=AggregationOperators.Count, fields=['id', 'name']) 
    & Agg(operator=AggregationOperators.Sum, fields='amount')
)

await directus.collection("transactions").aggregate(complex_aggregate).read()
```

Result

```
{'count': {'id': 184, 'email': 8}, 'sum': {'id': 1.7976931348623157e+308}}
```

## Full list of operators

| Operator           | Alt                | Description                         |
|--------------------|--------------------|-------------------------------------|
| `Count`            | `count`           | Count                               |
| `CountDistinct`    | `countDistinct`   | Count Distinctly                    |
| `CountAll`         | `countAll`        | Count All (Only in GraphQL)         |
| `Sum`              | `sum`             | Sum                                 |
| `SumDistinct`      | `sumDistinct`     | Sum Distinctly                      |
| `Average`          | `average`         | Average                             |
| `AverageDistinct`  | `averageDistinct` | Average Distinctly                  |
| `Minimum`          | `minimum`         | Minimum                             |
| `Maximum`          | `maximum`         | Maximum                             |
