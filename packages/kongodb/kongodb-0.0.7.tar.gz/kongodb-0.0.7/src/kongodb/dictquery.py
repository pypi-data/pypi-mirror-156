#-----------------------------
# -- fundb --
# dictquery module
#-----------------------------

from re import sub
from typing import Any, List
from . import lib 

# Map filter
# Map filter operators with their functions
QUERY_FILTERING_MAPPER = {
    '=': '_is_equal',
    'eq': '_is_equal',
    '!=': '_is_not_equal',
    'neq': '_is_not_equal',
    '>': '_is_greater',
    'gt': '_is_greater',
    '<': '_is_smaller',
    'lt': '_is_smaller',
    '>=': '_is_greater_equal',
    'gte': '_is_greater_equal',
    '<=': '_is_smaller_equal',
    'lte': '_is_smaller_equal',
    'in': '_is_in',
    'notin': '_is_not_in',
    'null': '_is_null',
    'notnull': '_is_not_null',
    'startswith': '_is_starts_with',
    'endswith': '_is_ends_with',
    'includes': '_is_includes',
    'between': "_is_between",
    'contains': '_is_contains'
}

# FILTER_OPERATOR:
FILTER_OPERATOR = ":$"

# SQL_OPERATORS: valid/strict operators for SQL
SQL_OPERATORS = {
    "eq": "= ?",
    "ne": "!= ?",
    "lt": "< ?",
    "gt": "> ? ",
    "lte": "<= ?",
    "gte": ">= ? ",
    "between": "BETWEEN ? AND ?",
}


"""
DictQuery

This library helps filter sub document in a list of dict 

:USAGE

data = List[dict]
data = [
    {
        "location": "USA",
        "age": 21,
        "email": "something@this.io",
        "friends": [
            {
                "name": "Jacob",
                "city": "Charlotte",

            }
        ]
    },
    ...
]


filters = {
    "location": "USA",
    "age:$gte": 18,
    "email:$endswith": ".io",
    "friends[*].city:$in": ["Charlotte", "Atlanta"]
}

filtered_data = DictQuery(data).execute(filter)

"""
class DictQuery(object):

    def __init__(self, data: list):

        if not isinstance(data, list):
            raise TypeError("Provided Data is not list")
        self._data = self._flatten_data_list(data)

    def execute(self, filters) -> list:
        self._reset_queries()
        self._build_queries(filters)
        return self._unflatten_data_list(self._execute_queries(self._data, self._queries))
 
    def _flatten_data_list(self, data):
        return [lib.flatten_dict(d) for d in data] if isinstance(data, list) else []

    def _unflatten_data_list(self, data):
        return [lib.unflatten_dict(d) for d in data] if isinstance(data, list) else []

    def _reset_queries(self):
        """ 
        Reset previous query data 
        """
        self._queries = []
        self._current_query_index = 0

    def _store_query(self, query_items):
        """Make where clause

        :@param query_items
        :@type query_items: dict
        """
        temp_index = self._current_query_index
        if len(self._queries) - 1 < temp_index:
            self._queries.append([])
        self._queries[temp_index].append(query_items)
 
    def _execute_queries(self, data:list, queries:list):
        """
        Args:
            data:list
        """
        _matcher = _Matcher()
       
        def func(item):
            or_check = False
            for queriesx in queries:
                and_check = True
                for query in queriesx:
                    _qk = query.get("key")

                    # Filter sub-list using `[*].` 
                    # /basepath/something[*].x
                    if "[*]." in _qk:    
                        and_check2 = False                    
                        basepath, subpath = _qk.split("[*].")
                        subdata = item.get(basepath)
                        if subdata:
                            for subitem in subdata:
                                and_check2 |= _matcher._match(
                                    subitem.get(subpath, None),
                                    query.get('operator'),
                                    query.get('value'),
                                    query.get('case_insensitive')
                                )    
                        and_check &= and_check2
                    
                    # regular query
                    else:
                        and_check &= _matcher._match(
                            item.get(_qk, None),
                            query.get('operator'),
                            query.get('value'),
                            query.get('case_insensitive')
                        )
                    
                or_check |= and_check
            return or_check

        return list(filter(lambda item: func(item), data))

    def _where(self, key, operator, value, case_insensitive=False):
        """Make where clause

        :@param key
        :@param operator
        :@param value
        :@type key,operator,value: string

        :@param case_insensitive
        :@type case_insensitive: bool

        :@return self
        """
        self._store_query({
            "key": key,
            "operator": operator,
            "value": value,
            "case_insensitive": case_insensitive
        })

        return self

    def _or_where(self, key, operator, value):
        """Make _or_where clause

        :@param key
        :@param operator
        :@param value
        :@type key, operator, value: string

        :@return self
        """
        if len(self._queries) > 0:
            self._current_query_index += 1
        self._store_query({"key": key, "operator": operator, "value": value})
        return self

    def _build_queries(self, filters: dict) -> tuple:
        """
        Create a FILTER clause

        Params:
            filters: dict
                {
                    'name': 'something',
                    'age:$gt': 18,
                    'cities:$in': ['charlotte', 'Concord'],
                    '$or': [
                        {
                            "cities:$in": [],
                            "_perms.read:$in":[] 
                        }
                    ]
                }
        """

        for k in filters:
            if k.startswith("$"):
                k_ = k.lower()
                # operation
                if k_ in ["$or"] and isinstance(filters[k], (dict, list)):
                    fk = filters[k]
                    if isinstance(fk, dict):
                        fk = [fk]
                    for k0 in fk:
                        for k2 in k0:
                            self._build_query_row(k2, k0[k2], _or=True)
                else:
                    raise Exception("Invalid logic: %s" % k)
            else:
                self._build_query_row(k, filters[k])

    def _build_query_row(self, k: str, value: Any, _or: bool = False):
        operator = "$eq"  # default operator
        if ":" in k:
            k, operator = k.split(":", 2)
            operator = operator.lower()
        operator = operator.replace("$", "")

        if _or:
            self._or_where(k, operator, value)
        self._where(k, operator, value)

class _Matcher(object):
    """docstring for Helper."""
    MAP = QUERY_FILTERING_MAPPER

    def _is_equal(self, x, y):
        return x == y

    def _is_not_equal(self, x, y):
        return x != y

    def _is_greater(self, x, y):
        return x > y

    def _is_smaller(self, x, y):
        return x < y

    def _is_greater_equal(self, x, y):
        return x >= y

    def _is_smaller_equal(self, x, y):
        return x <= y

    def _is_in(self, key, arr):
        return isinstance(arr, list) and \
            bool(len(([k for k in key if k in arr]
                 if isinstance(key, list) else key in arr)))

    def _is_not_in(self, key, arr):
        return isinstance(arr, list) and (key not in arr)

    def _is_null(self, x, y=None):
        return x is None

    def _is_not_null(self, x, y=None):
        return x is not None

    def _is_starts_with(self, data, val):
        if not isinstance(data, str):
            return False
        return data.startswith(val)

    def _is_ends_with(self, data, val):
        if not isinstance(data, str):
            return False
        return data.endswith(val)

    def _is_includes(self, ldata, val):
        if isinstance(ldata, (list, dict, str)):
            return val in ldata
        return False

    def _is_between(self, data, val):
        # TODO: IMPLEMENT
        return False
        
    def _is_contains(self, data, val):
        # TODO: IMPLEMENT
        return False



    def _to_lower(self, x, y):
        return [[v.lower() if isinstance(v, str) else v for v in val]
                if isinstance(val, list) else val.lower()
                if isinstance(val, str) else val
                for val in [x, y]]

    def _match(self, x, op, y, case_insensitive):
        """Compare the given `x` and `y` based on `op`

        :@param x, y, op, case_insensitive
        :@type x, y: mixed
        :@type op: string
        :@type case_insensitive: bool

        :@return bool
        :@throws ValueError
        """
        if (op not in self.MAP):
            raise ValueError('Invalid where condition given: %s' % op)

        if case_insensitive:
            x, y = self._to_lower(x, y)

        func = getattr(self, self.MAP.get(op))
        return func(x, y)

