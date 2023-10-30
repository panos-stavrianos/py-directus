# Aggregators

> NOTE: Temporary syntax

You can aggregate the data by defining the needed aggregation with the `Agg` class and passing it to the `aggregate` method

```python
from py_directus.aggregator import Agg

agg_obj = Agg(AggregationOperators.Count)

await directus.collection("directus_users").aggregate(agg_obj).read()
```

In case you need only certain fields

```python
from py_directus.aggregator import Agg

amount_agg = Agg(AggregationOperators.Sum, fields="amount")

await directus.collection("transactions").aggregate(amount_agg).read()
```

## Full list of operators

| Operator             | Description                         |
|----------------------|-------------------------------------|
| `Count`              | Count                               |
| `CountDistinct`      | Count Distinctly                    |
| `CountAll`           | Count All (Only in GraphQL)         |
| `Sum`                | Sum                                 |
| `SumDistinct`        | Sum Distinctly                      |
| `Average`            | Average                             |
| `AverageDistinct`    | Average Distinctly                  |
| `Minimum`            | Minimum                             |
| `Maximum`            | Maximum                             |
