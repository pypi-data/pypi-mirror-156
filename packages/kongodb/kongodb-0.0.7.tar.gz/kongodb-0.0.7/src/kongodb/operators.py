#-----------------------------
# -- kongodb --
# operators module
#-----------------------------

import re 
import copy
import arrow
from . import lib
from typing import Any, List


class UndefinedOperatorValue(object): pass


def _get_int_data(data: dict, path: str) -> int:
    v = lib.dict_get(data, path)
    if v is None:
        v = 0
    if not isinstance(v, int):
        raise TypeError("Invalid data type for '%s'. Must be 'int' " % path)
    return v


def _get_list_data(data: dict, path: str) -> list:
    v = lib.dict_get(data, path)
    if v is None:
        return []
    if not isinstance(v, list):
        raise TypeError("Invalid data type for '%s'. Must be 'list' " % path)
    return v


def _values_to_mlist(value, many=False):
    return [value] if many is False else value if isinstance(value, (list, tuple)) else [value]


def _arrow_date_shifter(dt:arrow.Arrow, stmt:str) -> arrow.Arrow:
    """
    To shift the Arrow date to future or past

    Args:
        dt:arrow.Arrow - 
        stmt:str - 
    Returns:
        arrow.Arrow

    
    Valid shift:
        YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, WEEKS
    
    Format: [[+/-][$NUMBER][$SHIFT][SPACE]... ]
        +1Days
        -3Hours 6Minutes
        +1Days 2Hours 3Minutes
        1Year 2Month +3Days 5Hours -6Minutes 3Seconds 5weeks
    """
    shifts = ["years", "months", "days", "hours", "minutes", "seconds", "weeks"]

    t = [t for t in  stmt.split(" ") if t.strip(" ")]
    t2 = [re.findall(r'((?:\+|\-)?(?:\d+))?(\w+)?', s)[0] for s in t if s]
    t2 = [(t[1].lower(), int(t[0])) for t in t2 if t[0] and t[1]]
    kw = {}
    for k, v in t2:
        if k in shifts or "%ss" % k in shifts:
            k = k if k.endswith("s") else "%ss" %k
            kw[k] = v
    if kw:
        dt = dt.shift(**kw)
        return dt

    return dt
 

def update_operations(data: dict, ops: dict):
    """
    Update Operations

    Args:
        data:dict - data to run $ops on 


    Returns:
        tuple(updated_data:dict, oplog)

    Operators:
        $incr
        $decr
        $unset
        $xadd - $xadd_many
        $xrem - $xrem_many
        $xpush - $xpush_many
        $xpushl - $xpushl_many
        $xpop
        $xpopl
        $timestamp - To update a timestamp. 
    
    Example
        {
           "key:$incr": True|1,
           "key:$decr": True|1,
           "some.key:$unset": True,
           "some.list:$xadd": Any,
           "some.list:$xadd_many": [Any, Any, Any, ...],
           "some.list:$xrem": Any,
           "some.list:$xrem_many": [Any, Any, Any, ...],     
           "some.list:$xpush": Any,
           "some.list:$xpush_many": [Any, Any, Any, ...],   
           "some.list:$xpushl": Any,
           "some.list:$xpushl_many": [Any, Any, Any, ...],    
           "some.list:$xpop": True,
           "some.list:$xpopl: False,
           "some.timestampfield:$timestamp": True,             
           "some.timestampfield:$timestamp": "+1Day +2Hours 5Minutes"             
        }
    """
    data = copy.deepcopy(data)
    oplog = {}
    for path, value in ops.items():
        if ":" in path:
            if ":$" not in path:
                continue

            oplog_path = path
            path, op = path.split(":$")

            # $incr
            if op == "incr":
                value = _get_int_data(data, path) + \
                    (value if isinstance(value, int) else 1)
                oplog[oplog_path] = value

            # $decr
            elif op == "decr":
                value = _get_int_data(data, path) - \
                    (value if isinstance(value, int) else 1)
                oplog[oplog_path] = value

            # $unset
            elif op == "unset":
                v = lib.dict_pop(
                    obj=data, path=path) if "." in path else data.pop(path)
                oplog[oplog_path] = v
                value = UndefinedOperatorValue()

            # $timestamp
            elif op == "timestamp":
                dt = lib.get_timestamp()
                if value is True:
                    value = dt
                else:
                    try:
                        if isinstance(value, str):
                            value = _arrow_date_shifter(dt=dt, stmt=value)
                        else:
                            value = UndefinedOperatorValue()
                    except: 
                         value = UndefinedOperatorValue()

            # LIST operators

            elif op in (
                "xadd", "xadd_many",
                "xrem", "xrem_many",
                "xpush", "xpush_many",
                "xpushl", "xpushl_many"
            ):
                values = _values_to_mlist(value, many=op.endswith("_many"))
                v = _get_list_data(data, path)

                # $xadd|$xadd_many
                if op.startswith("xadd"):
                    for val in values:
                        if val not in v:
                            v.append(val)
                    value = v

                # $xrem|$xrem_many
                elif op.startswith("xrem"):
                    _removed = False
                    for val in values:
                        if val in v:
                            _removed = True
                            v.remove(val)
                    if not _removed:
                        value = UndefinedOperatorValue()

                # $xpush|$xpush_many
                elif op in ("xpush", "xpush_many"):
                    v.extend(values)
                    value = v

                # $xpushl|$xpushl_many
                elif op in ("xpushl", "xpushl_many"):
                    v2 = list(values)
                    v2.extend(v)
                    value = v2

            # $xpop
            elif op == "xpop":
                v = _get_list_data(data, path)
                if len(v):
                    value = v[:-1]
                    oplog[oplog_path] = v[-1]

            # $xpopl
            elif op == "xpopl":
                v = _get_list_data(data, path)
                if len(v):
                    value = v[1:]
                    oplog[oplog_path] = v[0]


            # UndefinedOperatorValue
            else:
                value = UndefinedOperatorValue()


        if not isinstance(value, UndefinedOperatorValue):
            lib.dict_set(obj=data, path=path, value=value)

    return data, oplog

