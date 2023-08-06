# -----------------------------
# -- kongodb --
# database module
# -----------------------------


from urllib.parse import urlparse
from typing import Any, List, Union
from . import adapters, lib, cursor, jsonquery, types, operators


SQL_DATETIME_FORMAT = "YYYY-MM-DD HH:mm:ss"


class Database(object):
    """
    :: Database

    Class to create a connection to an adapter and select a container
    """

    def __init__(self, dsn_adapter: Union[str, adapters.BaseAdapter]):
        """
        Connect database 

        Return:
            dsn: str
                *`scheme://hostname` should be there at minimum
                - sqlite://
                - sqlite://./file.db
                - mysql://username:password@hostname:port/dbname
                - mariadb://username:password@hostname:port/dbname
        """
        if isinstance(dsn_adapter, adapters.BaseAdapter):
            self.db = dsn_adapter
        elif isinstance(dsn_adapter, str):
            # adapters.SQLiteAdapter(file=":memory:")
            _ = urlparse(dsn_adapter)
            # scheme, username, password, hostname, port, path.strip("/")
            if _.scheme == "sqlite":
                self.db = adapters.SQLiteAdapter(dsn_adapter)
            elif _.scheme in ["mysql", "mariadb"]:
                self.db = adapters.MySQLAdapter(dsn_adapter)

    def container(self, name: str, columns: list = None):
        """
        Select a container

        Args:
            name: str - container name
            columns: list - list of columns and indexes to add

        Returns:
            Container
        """
        container = Container(self.db, name)
        if columns:
            container.add_columns(columns)
        return container

    def drop_container(self, name):
        """
        Drop/Delete a table/container

        Returns:
            None
        """
        self.db.drop_container(name)

    @property
    def containers(self) -> list:
        """
        List containers in the database

        Returns: 
          list
        """
        return self.db.get_containers()

    @staticmethod
    def utcnow():
        return lib.get_timestamp()


class Item(dict):
    """
    Item/ActiveRecord

    Every row is a document in Kongodb
    """

    def __init__(self, container, row: dict):
        self.container = container
        self._load(row)


    def get(self, path: str, default: Any = None) -> Any:
        """
        GET: Return a property by key/DotNotation

        ie: 
            #get("key.deep1.deep2.deep3")

        Args:
            path:str - the dotnotation path
            default:Any - default value 

        Returns:
            Any
        """
        return lib.dict_get(obj=dict(self), path=path, default=default)

    def set(self, path: str, value: Any):
        """
        SET: Set a property by key/DotNotation

        Args:
            path:str - the dotnotation path
            value:Any - The value

        Returns:
            Void
        """
        self._update({path : value })

    def len(self, path: str):
        """
        Get the length of the items in a str/list/dict
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed
        """
        v = self.get(path)
        return len(v) if v else 0

    def unset(self, path: str):
        """ 
        UNSET: Remove a property by key/DotNotation and return the value

        Args:
            path:str

        Returns:
            Any: the value that was removed
        """
        self._update({ path + ":$unset" % path: True })
        
    def update(self, data:dict):
        """
        UPDATE: Update the active Item

        Returns:
            Item
        """
        self._update(data)

    def delete(self):
        """
        DELETE: Delete the Doument from the container

        Returns:
            None
        """
        self.container.delete_id(self._id)
        self._clear_self()

    # ---

    def incr(self, path: str, incr=1):
        """
        INCR: increment a value by 1
        Args
            path:str - path
            incr:1 - value to inc by
        Returns:    
            int - the value that was incremented
        """
        op = "%s:$incr" % path
        oplog = self._update({op: incr })
        return oplog.get(op)

    def decr(self, path: str, decr=1):
        """
        DECR: decrement a value by 1
        Args
            path:str - path
            decr:1 - value to dec by
        Returns:    
            int - the value that was decremented
        """
        op = "%s:$decr" % path
        oplog = self._update({op: decr })
        return oplog.get(op)

    def xadd(self, path: str, values):
        """
        LADD: Add *values if they don't exist yet

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xadd" % path
        self._update({op: values })

    def xadd_multi(self, path: str, *values: List[Any]):
        """
        LADD: Add *values if they don't exist yet

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xadd_multi" % path
        self._update({op: values })

    def xrem(self, path: str, values):
        """
        LREM: Remove items from a list

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xrem" % path
        oplog = self._update({op: values })
        return oplog.get(op)

    def xrem_multi(self, path: str, *values: List[Any]):
        """
        LREM: Remove items from a list

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xrem_multi" % path
        oplog = self._update({op: values })
        return oplog.get(op)

    def xpush(self, path: str, values:Any):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpush" % path
        self._update({op: values })

    def xpush_multi(self, path: str, *values: List[Any]):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpush_multi" % path
        self._update({op: values })

    def lpushl(self, path: str, *values: List[Any]):
        """
        LPUSHL: push item to the left

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        v = self._req_list_prop(path)
        v2 = list(values)
        v2.extend(v)
        self.set(path=path, value=v2)
        return self.get(path)

    def lpop(self, path: str):
        """
        Remove value at the end an array/list
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed

        """
        op = "%s:$xpop" % path
        oplog = self._update({op: True })
        return oplog.get(op)

    def lpopl(self, path: str):
        """
        Remove value at the beginning an array/list
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed        
        """
        op = "%s:$xpopl" % path
        oplog = self._update({op: True })
        return oplog.get(op)


    # --- misc
    def save(self):
        """
        To commit the data when it's mutated outside.
            doc = Item()
            doc["xone"][1] = True
            doc.save()
        """
        data = dict(self)
        self.update(data)

    def _update(self, ops:dict):
        """
        Return oplog
        """
        data = dict(self)
        doc, oplog = operators.update_operations(data, ops)
        row = self.container.update_id(_id=self._id, doc=doc, _as_document=False)
        self._load(row)
        return oplog

    def _load(self, row: dict):
        """
        load the content into the document

        Args:
            row: dict
        """
        self._clear_self()
        row = _parse_row(row)
        self._id = row.get("_id")
        super().__init__(row)

    def _clear_self(self):
        """ clearout all properties """
        for _ in list(self.keys()):
            if _ in self:
                del self[_]


class Container(object):
    """
    Container/Table

    """

    DEFAULT_COLUMNS = ["_id", "_json", "_created_at", "_modified_at"]
    _columns = []
    _indexes = []

    def __init__(self, conn: adapters.BaseAdapter, name):
        self.name = name
        self.db = conn
        self.db.create_container(self.name)

    def __len__(self):
        return self.size

    # ---- properties ----

    @property
    def columns(self) -> list:
        """ 
        Get the list of all the columns name

        Returns:
            list
        """
        return self.db.get_columns(self.name)

    @property
    def indexes(self) -> list:
        """
        Get the list of all indexes

        Returns:
            list
        """
        return self.db.get_indexes(self.name)

    @property
    def size(self) -> int:
        """
        Get the total entries in the container

        Returns:
            int
        """
        return self.db.get_size(self.name)

    # ---- methods ----

    def get(self, _id: str) -> Item:
        """
        Get a document by _id
        Alias to find_one(_id)

        Returns:
            Item
        """
        return self.find_one(_id=_id)

    def find_one(self, *a, **kw) -> Item:
        """
        Retrieve 1 document by _id, or other filters

        Args:
          _id:str - the document id
          _as_document:bool - when True return Item
          **kw other query

        Returns:
          Item

        Examples:
            #.find_one()
            #.find_one('IDfyeiquyteqtyqiuyt')
            #.find_one(_id="ID....")
            #.find_one(key1=value1, key2=value2, ...)
            #.find_one({key: val, key2: val2, ...})

        """

        _as_document = True
        if "_as_document" in kw:
            _as_document = kw.pop("_as_document")

        # expecting the first arg to be _id
        filters = {"_id": a[0]} if a else kw

        r = self.find(filters=filters, limit=1, _as_document=_as_document)
        return r[0] if len(r) else None

    def find_all(self, *a, **kw) -> List[Item]:
        """
        Retrieve all docuemts based on criteria return in a list

        Returns:
            List[Item]
        """
        return list(self.find(*a, **kw))

    def find(self, filters: dict = {}, sorts:dict = {}, limit: int = 10, skip: int = 0, _as_document=True) -> cursor.Cursor:
        """
        To fetch data from the container

        Smart Query
          Allow to use primary indexes from sqlite 
          then do the xtra from parsing the documents

        Args:
          filters:dict - 
          sort:dict - {key: "DESC", key2: "ASC"}
          limit:int - 
          skit:int - 

        Returns:
          cursor.Cursor
        """

        # SMART QUERY
        # Do the primary search in the columns
        # If there is more search properties, take it to the json
        xparams = []
        xquery = []
        
        smart_filters = _parse_smart_filtering(
            filters, indexed_columns=self.columns)

        # Build the SQL query
        query = "SELECT * FROM %s " % self.name

        # Indexed filtering
        if smart_filters["SQL_FILTERS"]:
            for f in smart_filters["SQL_FILTERS"]:
                xquery.append(" %s %s" % (f[0], f[1]))
                if isinstance(f[2], list):
                    for _ in f[2]:
                        xparams.append(_)
                else:
                    xparams.append(f[2])
        if xquery and xparams:
            query += " WHERE %s " % " AND ".join(xquery)

        # Perform JSON search, as we have JSON_FILTERS
        # Full table scan, relative to WHERE clause
        chunk = 100
        data = []
        if smart_filters["JSON_FILTERS"]:
            for chunked in self.db.fetchmany(query, xparams, chunk):
                if chunked:
                    rows = [_parse_row(row) for row in chunked]
                    for r in jsonquery.execute(rows, smart_filters["JSON_FILTERS"]):
                        data.append(r)
                else:
                    break
            if data:
                if _as_document:
                    data = [Item(self, d) for d in data]
            sorts = _parse_sort_dict(sorts, False)
            return cursor.Cursor(data, sort=sorts, limit=limit, skip=skip)

        # Skip JSON SEARCH, use only SQL.
        # No need to look into the JSON. The DB is enough
        else:
            # order by
            sorts = _parse_sort_dict(sorts, True)
            if sorts:
                query += " ORDER BY "
                query += " ".join([" %s %s " % (_[0], _[1]) for _ in sorts])

            # limit/skip
            if limit or skip:
                query += " LIMIT ?, ?"
                xparams.append(skip or 0)
                xparams.append(limit or 10)

            res = self.db.fetchall(query, xparams)
            if _as_document:
                data = [Item(self, row) for row in res]
            else:
                data = list(res)
            return cursor.Cursor(data)

    def add(self, doc: dict, _as_document: bool = True) -> Item:
        """
        Add a new document in container

        use Smart Insert, by checking if a value in the doc in is a column.

        Args:
          doc:dict - Data to be inserted

        Returns:
            Item
        """
        if not isinstance(doc, dict):
            raise TypeError('Invalid data type. Must be a dict')

        _id = lib.gen_id()
        ts = lib.get_timestamp()
        f_ts = ts.format(SQL_DATETIME_FORMAT)
        doc.update({
            "_id": _id,
            "_created_at": ts,
            "_modified_at": ts,
        })

        xcolumns = ["_id", "_json", "_created_at", "_modified_at"]
        xparams = [_id, lib.json_dumps(doc), f_ts, f_ts]
        q = "INSERT INTO %s " % self.name

        # indexed data
        # some data can't be overwritten
        for col in self.columns:
            if col in doc and col not in xcolumns:
                xcolumns.append(col)
                xparams.append(doc[col])

        q += " ( %s ) VALUES ( %s ) " % (",".join(xcolumns),
                                         ",".join(["?" for _ in xparams]))

        self.db.execute(q, xparams)
        return self.find_one(_id=_id, _as_document=_as_document)

    def update(self, filters): raise NotImplementedError()
    def delete(self, filters): raise NotImplementedError()

    def update_id(self, _id: str, doc: dict = {}, replace: bool = False, _as_document=True) -> Item:
        """
        To update a document

        Args:
          _id:str - document id
          doc:dict - the document to update
          replace:bool - By default document will be merged with existing data
                  When True, it will save it as is. 

        Returns:
            Item
        """
        rdoc = self.find_one(_id=_id, _as_document=False)
        if rdoc:
            ts = lib.get_timestamp()
            ts_f = ts.format(SQL_DATETIME_FORMAT)
            _doc = doc if replace else lib.dict_merge(
                lib.json_loads(rdoc["_json"]), doc)
            _doc["_modified_at"] = ts
            _restricted_columns = self.DEFAULT_COLUMNS[:]

            xcolumns = ["_json", "_modified_at"]
            xparams = [lib.json_dumps(_doc), ts_f]

            q = "UPDATE %s SET " % self.name

            # indexed data
            # some data can't be overriden
            for col in self.columns:
                if col in _doc and col not in _restricted_columns:
                    xcolumns.append(col)
                    xparams.append(_doc[col])
            q += ",".join(["%s = ?" % _ for _ in xcolumns])
            q += " WHERE _id=?"
            xparams.append(_id)
            self.db.execute(q, xparams)
            return self.find_one(_id=_id, _as_document=_as_document)
        return None

    def delete_id(self, _id: str) -> bool:
        """
        To delete an entry by _id

        Args:
            _id:str - entry id

        Returns:
            Bool
        """
        self.db.execute("DELETE FROM %s WHERE _id=?" % (self.name), (_id, ))
        return True

    def add_columns(self, columns: list, enforce_index=False):
        """
        To add columns. With options to add indexes

        Args:
            columns: List[str|types.BaseType]
        """
        cols_stmt = []
        for stmt in columns:
            if isinstance(stmt, types.BaseType):
                cols_stmt.append(stmt)
            elif isinstance(stmt, str):
                cols_stmt.append(types.stmt_to_fieldtype(stmt))

        self.db.add_columns(table=self.name, cols_stmt=cols_stmt)

    def add_indexes(self, columns: List[str]):
        """
        To indexed columns

        Args: 
            columns:
                List[str]. Documentation-> #add_columns
        """
        self.add_columns(columns=columns, enforce_index=True)

    # TODO:
    # def insert_many(self, data:List[dict])
    # def update_many(self, data:dict, filters:dict)
    # def delete_many()



def _parse_smart_filtering(filters: dict, indexed_columns: list = []) -> dict:
    """
    Smart Filter
    Breaks down the filters based on type. 
    - SQL_FILTERS: is more restrictive on what can be queried. 
                  Will be done at the SQL level
    - JSON_FILTERS: is more loose. 
                    It contains items that are not in the sql_filters. 
                    Will be done at the JSON level

    Args:
      filters: dict  - 
      indexed_columns: list - List of indexed sql columns/or other columns in the table 
                       this will allow with the smart filtering

    Returns: 
      dict:
        SQL_FILTERS
        JSON_FILTERS
    """

    # filter SQL_OPERATORS filters
    sql_filters = []
    json_filters = {}
    for k, v in filters.items():
        if jsonquery.FILTER_OPERATOR in k:
            f, op = k.split(jsonquery.FILTER_OPERATOR)
            if f in indexed_columns and op in jsonquery.SQL_OPERATORS:
                sql_filters.append((f, jsonquery.SQL_OPERATORS[op], v))
                continue
        else:
            if k in indexed_columns:
                sql_filters.append((k, jsonquery.SQL_OPERATORS["eq"], v))
                continue
        json_filters[k] = v

    return {
        "SQL_FILTERS": sql_filters,
        "JSON_FILTERS": json_filters
    }


def _parse_row(row: dict) -> dict:
    """
    Convert a result row to dict, by merging _json with the rest of the columns

    Args:
        row: dict

    Returns
        dict
    """
    row = row.copy()
    _json = lib.json_loads(row.pop("_json")) if "_json" in row else {}
    return {
        **row,  # ensure columns exists
        **_json
    }

def _ascdesc(v, as_str=True):
    if as_str:
        if isinstance(v, int):
            return "DESC" if v == -1 else "ASC" 
    else:
        if isinstance(v, str):
            return -1 if v.upper() == "DESC" else 1
    return v

def _parse_sort_dict(sorts:dict, as_str=True):
    return [(k, _ascdesc(v, as_str)) for k,v in sorts.items()]

