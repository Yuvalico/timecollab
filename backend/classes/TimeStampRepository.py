from models import *
from classes.User import User
from typing import List
import bcrypt
from cmn_utils import print_exception, datetime2iso, iso2datetime
from cmn_defs import *
from classes.User import User
from classes.TimeStamp import TimeStamp
from classes.RC import RC


class TimeStampRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all_timestamps(self) -> List[TimeStamp]:
        timestamps = TimeStampModel.query.all()
        return [timestamp.to_class() for timestamp in timestamps]

    def get_timestamp_by_uuid(self, uuid: str) -> TimeStamp|RC:
        timestamp = TimeStampModel.query.get(uuid)
        if timestamp:
            return timestamp.to_class()
        return RC(E_RC.RC_NOT_FOUND, "Time stamp not found")
    
    def create_timestamp(self, email, entered_by_user, punch_type, punch_in, punch_out, reporting_type, detail) -> TimeStamp:
        if punch_in:
            punch_in_datetime = iso2datetime(punch_in) if not isinstance(punch_in, datetime) else punch_in
        if punch_out:
            punch_out_datetime= iso2datetime(punch_out) if not isinstance(punch_out, datetime) else punch_out
        try:
            if not punch_in and not punch_out:
                punch_in_timestamp = datetime.now(timezone.utc)
                new_timestamp = TimeStamp(
                    user_email=email,
                    entered_by=entered_by_user,
                    punch_type=punch_type,
                    punch_in_timestamp=punch_in_timestamp,
                    reporting_type=reporting_type,
                    detail=detail
                )
        
            elif punch_in and not punch_out:
                new_timestamp = TimeStamp(
                    user_email=email,
                    entered_by=entered_by_user,
                    punch_type=punch_type,
                    punch_in_timestamp=punch_in_datetime,
                    reporting_type=reporting_type,
                    detail=detail
                )

            elif punch_in and punch_out:
                if punch_in_datetime > punch_out_datetime:
                    return RC(E_RC.RC_INVALID_INPUT, 'Start time should be earlier than end time')
                
                new_timestamp = TimeStamp(
                    user_email=email,
                    entered_by=entered_by_user,
                    punch_type=punch_type,
                    punch_in_timestamp=punch_in_datetime,
                    punch_out_timestamp=punch_out_datetime,
                    reporting_type=reporting_type,
                    detail=detail
                )
            
            else:
                return RC(E_RC.RC_INVALID_INPUT, 'Start time should be earlier than end time')

            new_timestamp_model = new_timestamp.to_model()
            db.session.merge(new_timestamp_model)
            db.session.commit()
            return new_timestamp
        
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def punch_out(self, email, reporting_type, detail) -> RC:
        try:
            today = datetime.now(timezone.utc).date()
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

            timestamp: TimeStampModel = TimeStampModel.query.filter(
                TimeStampModel.user_email == email,
                TimeStampModel.punch_in_timestamp >= start_of_day,
                TimeStampModel.punch_in_timestamp <= end_of_day,
                TimeStampModel.punch_out_timestamp == None
            ).order_by(TimeStampModel.punch_in_timestamp.desc()).first()

            if timestamp:
                timestamp.punch_out_timestamp = datetime.now(timezone.utc)
                timestamp.reporting_type = reporting_type
                timestamp.detail = detail
                
                db.session.commit()
                return RC(E_RC.RC_OK, 'Punched out successfully')
            else:
                return RC(E_RC.RC_INVALID_INPUT, 'No punch-in found for today. Please manually add a punch-in entry.\naction_required manual_punch_in')
                
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def edit_timestamp(self, timestamp: TimeStamp, entered_by_user: str, punch_type: str, punch_in: str, punch_out: str, reporting_type: str, detail: str) -> RC:
         try:
            if punch_in:
                try:
                    punch_in_timestamp = iso2datetime(punch_in)
                    timestamp.punch_in_timestamp = punch_in_timestamp.replace(tzinfo=timezone.utc)
                except ValueError:
                    return RC(E_RC.RC_INVALID_INPUT, 'Invalid punch_in_timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)')
            if punch_out:
                try:
                    punch_out_timestamp = iso2datetime(punch_out)
                    timestamp.punch_out_timestamp = punch_out_timestamp.replace(tzinfo=timezone.utc)
                except ValueError:
                    return RC(E_RC.RC_INVALID_INPUT, 'Invalid punch_out_timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS.ffffff) or null')
            if punch_type:
                timestamp.punch_type = punch_type
            if detail:
                timestamp.detail = detail
                
            if reporting_type:
                timestamp.reporting_type = reporting_type

            timestamp.entered_by = entered_by_user
            
            new_timestamp_model = timestamp.to_model()
            db.session.merge(new_timestamp_model)
            db.session.commit()
            return RC(E_RC.RC_OK, f"Time Stamp {timestamp.uuid} Updated Successfully")
         
         except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def delete_timestamp(self, uuid: str) -> RC:
         try:
            timestamp_to_del = TimeStampModel.query.filter_by(uuid=uuid).first()
            db.session.delete(timestamp_to_del)
            db.session.commit()
            return RC(E_RC.RC_OK, f"Time Stamp {uuid} Deleted Successfully")
         
         except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def check_punch_in_status(self, email) -> bool|RC:
        try:
            today = datetime.now(timezone.utc).date()
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

            timestamp = TimeStampModel.query.filter(
                TimeStampModel.user_email == email,
                TimeStampModel.punch_in_timestamp >= start_of_day,
                TimeStampModel.punch_in_timestamp <= end_of_day,
                TimeStampModel.punch_out_timestamp == None
            ).order_by(TimeStampModel.punch_in_timestamp.desc()).first()

            if timestamp:
                return True
            else:
                return False
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def get_range(self, start_date_str: str, end_date_str: str, email: str = None, company_id: str = None) -> list|RC:
        try:
            if not email or not start_date_str or not end_date_str:
                return RC(E_RC.RC_INVALID_INPUT, 'Missing start_date or end_date') 

            try:
                if not isinstance(start_date_str, datetime):
                    start_date = iso2datetime(start_date_str)
                else:
                    start_date = start_date_str
                    
                if not isinstance(end_date_str, datetime):    
                    end_date = iso2datetime(end_date_str)
                else:
                    end_date = end_date_str
                    
            except ValueError:
                return RC(E_RC.RC_INVALID_INPUT, 'Invalid date format. Use ISO format (YYYY-MM-DD)')
            
            if end_date < start_date:
                return RC(E_RC.RC_INVALID_INPUT, 'Start date must earlier than end date')
                
            # Fetch timestamps for the user
            if company_id is None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(
                    TimeStampModel.user_email == email,
                    TimeStampModel.punch_in_timestamp >= start_date,
                    TimeStampModel.punch_in_timestamp <= end_date
                ).all()
            elif company_id is not None:
                timestamps: TimeStampModel= TimeStampModel.query.filter(TimeStampModel.punch_in_timestamp >= start_date,
                            TimeStampModel.punch_in_timestamp <= end_date).join(User, TimeStampModel.user_email == UserModel.email)\
                            .filter(User.company_id == company_id).all()
                
            return [timestamp.to_class() for timestamp in timestamps]
                
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")