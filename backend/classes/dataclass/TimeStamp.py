from datetime import datetime
from classes.dataclass.User import User
from cmn_utils import *
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from classes.dataclass.BaseDomainClass import BaseDomainClass



@dataclass
class TimeStamp(BaseDomainClass):
    user_email: str
    entered_by: str
    punch_type: int
    punch_in_timestamp: datetime
    detail: str
    reporting_type: str
    punch_out_timestamp: datetime = None
    uuid: str = None
    total_work_time: int = None
    last_update: datetime = None
    user: User = None

    def to_dict(self):
        return {
            'uuid': str(self.uuid),
            'user_email': str(self.user_email),
            'entered_by': str(self.entered_by),
            'punch_type': self.punch_type,
            'punch_in_timestamp': datetime2iso(self.punch_in_timestamp),
            'punch_out_timestamp': datetime2iso(self.punch_out_timestamp),
            'reporting_type': self.reporting_type,
            'detail': self.detail,
            'total_work_time': self.total_work_time,
            'last_update': datetime2iso(self.last_update),
        }
        
    def to_model(self):
        from models import TimeStampModel
        return TimeStampModel(
            uuid =  self.uuid if self.uuid else None,
            user_email =  self.user_email,
            entered_by =  self.entered_by,
            punch_type =  self.punch_type,
            punch_in_timestamp =  iso2datetime(self.punch_in_timestamp) if not isinstance(self.punch_in_timestamp, datetime) else self.punch_in_timestamp,
            punch_out_timestamp =  iso2datetime(self.punch_out_timestamp) if not isinstance(self.punch_out_timestamp, datetime) else self.punch_out_timestamp,
            reporting_type =  self.reporting_type,
            detail =  self.detail,
            last_update =  self.last_update,
        )
