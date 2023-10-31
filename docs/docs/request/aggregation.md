# Aggregators

> NOTE: Temporary syntax

```python
Agg(AggregationOperators.Count, fields="id")

# OR

Agg("id__count")
```

## Usage

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

amount_agg = Agg(AggregationOperators.Sum, fields="amount")

await directus.collection("transactions").aggregate(amount_agg).read()
```

## Complex Aggregation

```python
from py_directus.aggregator import Agg
from py_directus.operators import AggregationOperators

complex_aggregate = (
    Agg(AggregationOperators.Count, fields=['id', 'name']) 
    & Agg(AggregationOperators.Sum, fields='amount')
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
| `Count`            | `_count`           | Count                               |
| `CountDistinct`    | `_countDistinct`   | Count Distinctly                    |
| `CountAll`         | `_countAll`        | Count All (Only in GraphQL)         |
| `Sum`              | `_sum`             | Sum                                 |
| `SumDistinct`      | `_sumDistinct`     | Sum Distinctly                      |
| `Average`          | `_average`         | Average                             |
| `AverageDistinct`  | `_averageDistinct` | Average Distinctly                  |
| `Minimum`          | `_minimum`         | Minimum                             |
| `Maximum`          | `_maximum`         | Maximum                             |
