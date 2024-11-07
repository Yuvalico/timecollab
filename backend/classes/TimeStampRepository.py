from models import *
from typing import List
from cmn_utils import print_exception, datetime2iso, iso2datetime
from classes.TimeStamp import TimeStamp
from classes.RC import RC, E_RC
from classes.BaseRepository import BaseRepository


class TimeStampRepository(BaseRepository):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_all_timestamps(self) -> List[TimeStamp]:
        timestamps = TimeStampModel.query.all()
        return [timestamp.to_class() for timestamp in timestamps]

    def get_timestamp_by_uuid(self, uuid: str) -> TimeStamp|RC:
        timestamp = TimeStampModel.query.get(uuid)
        if timestamp:
            return timestamp.to_class()
        return RC(E_RC.RC_NOT_FOUND, "Time stamp not found")
    
    # def create_timestamp(self, new_timestamp: TimeStamp) -> RC:
    #     try:

    #         new_timestamp_model = new_timestamp.to_model()
    #         return self._save(new_timestamp_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def punch_out(self, timestamp: TimeStamp) -> RC:
    #     try:
    #             return self._update(timestamp)
            
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def edit_timestamp(self, timestamp: TimeStamp, entered_by_user: str, punch_type: str, punch_in: str, punch_out: str, reporting_type: str, detail: str) -> RC:
    #      try:
    #         if punch_in:
    #             try:
    #                 punch_in_timestamp = iso2datetime(punch_in)
    #                 timestamp.punch_in_timestamp = punch_in_timestamp.replace(tzinfo=timezone.utc)
    #             except ValueError:
    #                 return RC(E_RC.RC_INVALID_INPUT, 'Invalid punch_in_timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)')
    #         if punch_out:
    #             try:
    #                 punch_out_timestamp = iso2datetime(punch_out)
    #                 timestamp.punch_out_timestamp = punch_out_timestamp.replace(tzinfo=timezone.utc)
    #             except ValueError:
    #                 return RC(E_RC.RC_INVALID_INPUT, 'Invalid punch_out_timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff) or null')
    #         if punch_type:
    #             timestamp.punch_type = punch_type
    #         if detail:
    #             timestamp.detail = detail
                
    #         if reporting_type:
    #             timestamp.reporting_type = reporting_type

    #         timestamp.entered_by = entered_by_user
            
    #         new_timestamp_model = timestamp.to_model()
    #         return self._update(new_timestamp_model)
         
    #      except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def delete_timestamp(self, uuid: str) -> RC:
    #      try:
    #         timestamp_to_del = TimeStampModel.query.filter_by(uuid=uuid).first()
    #         return self._delete(timestamp_to_del)
         
    #      except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def check_punch_in_status(self, email, start_of_day, end_of_day) -> bool|RC|None:
        try:
            
            timestamp: TimeStampModel = TimeStampModel.query.filter(
                TimeStampModel.user_email == email,
                TimeStampModel.punch_in_timestamp >= start_of_day,
                TimeStampModel.punch_in_timestamp <= end_of_day,
                TimeStampModel.punch_out_timestamp == None
            ).order_by(TimeStampModel.punch_in_timestamp.desc()).first()

            if timestamp:
                return timestamp.to_class()
            else:
                return None
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def get_range(self, start_date: datetime, end_date: datetime, email: str = None, company_id: str = None) -> list|RC:
        try:
            
            if company_id is None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(
                    TimeStampModel.user_email == email,
                    TimeStampModel.punch_in_timestamp >= start_date,
                    TimeStampModel.punch_in_timestamp <= end_date
                ).all()
            elif company_id is not None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(TimeStampModel.punch_in_timestamp >= start_date,
                            TimeStampModel.punch_in_timestamp <= end_date).join(UserModel, TimeStampModel.user_email == UserModel.email)\
                            .filter(UserModel.company_id == company_id).all()
                
            return [timestamp.to_class() for timestamp in timestamps]
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")