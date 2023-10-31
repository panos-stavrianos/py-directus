from enum import Enum


FILTER_OPERATORS = {
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


class AggregationOperators(str, Enum):
    Count = "count"
    CountDistinct = "countDistinct"
    CountAll = "countAll"
    Sum = "sum"
    SumDistinct = "sumDistinct"
    Average = "avg"
    AverageDistinct = "avgDistinct"
    Minimum = "min"
    Maximum = "max"

AGGREGATION_OPERATORS = {
    "_count": AggregationOperators.Count,
    "_countDistinct": AggregationOperators.CountDistinct,
    "_countAll": AggregationOperators.CountAll,
    "_sum": AggregationOperators.Sum,
    "_sumDistinct": AggregationOperators.SumDistinct,
    "_avg": AggregationOperators.Average,
    "_avgDistinct": AggregationOperators.AverageDistinct,
    "_min": AggregationOperators.Minimum,
    "_max": AggregationOperators.Maximum
}
