from sqlalchemy.schema import Table
from sqlalchemy import Column, String, Integer
from sqlalchemy import String
from sqlalchemy_bigquery import DATETIME
import config
from sqlalchemy.orm import registry

class Base():
    pass

mapper_registry = registry()

class LookupCodes():
    __table__ = "lookup_codes"
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "value": self.value,
            "last_update_datetime": self.last_update_datetime
        }
    
mapper_registry.map_imperatively(LookupCodes, Table(
       "lookup_codes",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True),
        Column("code", String),
        Column("value", String),
        Column("last_update_datetime", DATETIME(timezone=True))
))