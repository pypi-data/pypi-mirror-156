from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict
from typing import List, Union, Tuple, Optional
from datetime import datetime

from runtype import dataclass

DbPath = Tuple[str, ...]
DbKey = Union[int, str, bytes]
DbTime = datetime


class ColType:
    pass


@dataclass
class PrecisionType(ColType):
    precision: Optional[int]
    rounds: bool


class TemporalType(PrecisionType):
    pass


class Timestamp(TemporalType):
    pass


class TimestampTZ(TemporalType):
    pass


class Datetime(TemporalType):
    pass


@dataclass
class UnknownColType(ColType):
    text: str


class AbstractDatabase(ABC):
    @abstractmethod
    def quote(self, s: str):
        "Quote SQL name (implementation specific)"
        ...

    @abstractmethod
    def to_string(self, s: str) -> str:
        "Provide SQL for casting a column to string"
        ...

    @abstractmethod
    def md5_to_int(self, s: str) -> str:
        "Provide SQL for computing md5 and returning an int"
        ...

    @abstractmethod
    def _query(self, sql_code: str) -> list:
        "Send query to database and return result"
        ...

    @abstractmethod
    def select_table_schema(self, path: DbPath) -> str:
        "Provide SQL for selecting the table schema as (name, type, date_prec, num_prec)"
        ...

    @abstractmethod
    def query_table_schema(self, path: DbPath) -> Dict[str, ColType]:
        "Query the table for its schema for table in 'path', and return {column: type}"
        ...

    @abstractmethod
    def parse_table_name(self, name: str) -> DbPath:
        "Parse the given table name into a DbPath"
        ...

    @abstractmethod
    def close(self):
        "Close connection(s) to the database instance. Querying will stop functioning."
        ...

    @abstractmethod
    def normalize_value_by_type(self, value: str, coltype: ColType) -> str:
        """Creates an SQL expression, that converts 'value' to a normalized representation.

        The returned expression must accept any SQL value, and return a string.

        - Dates are expected in the format:
            "YYYY-MM-DD HH:mm:SS.FFFFFF"

            Rounded up/down according to coltype.rounds

        """
        ...
