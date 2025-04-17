import pytz
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, Text, JSON, Enum as SQLAlchemyEnum, Float, func, DateTime
)
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class DefaultTimeStamp(Base):
    """
    Default time-stamped model with `created_at` and `updated_at`.
    This is inherited by all other models to standardize timestamp handling.
    """
    __abstract__ = True  # This class will not create a table itself

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    @hybrid_property
    def created_at_ist(self):
        """Return the created_at timestamp in IST."""
        return self.convert_to_ist(self.created_at)

    @hybrid_property
    def updated_at_ist(self):
        """Return the updated_at timestamp in IST."""
        return self.convert_to_ist(self.updated_at)

    def convert_to_ist(self, utc_dt):
        """Convert UTC datetime to IST."""
        if utc_dt.tzinfo is None:  # If naive datetime
            utc_dt = pytz.utc.localize(utc_dt)
        ist_zone = pytz.timezone('Asia/Kolkata')
        return utc_dt.astimezone(ist_zone)


class Rule(DefaultTimeStamp):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_config = Column(JSON, nullable=True)
    is_enabled = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

class Business(DefaultTimeStamp):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    business_sector = Column(String(255), nullable=True)
    risk_score = Column(String(255), nullable=True)
    risk_response = Column(JSON, nullable=True)
    response_computed_on = Column(DateTime, nullable=True)


class DocumentData(DefaultTimeStamp):
    __tablename__ = "document_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(255), nullable=False)
    raw_response = Column(JSON, nullable=True)
    business_id = Column(Integer)


class FeatureFlag(DefaultTimeStamp):
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, unique=True,autoincrement=True)
    name = Column(String, index=True, unique=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, nullable=True)  # Stores additional settings as JSON

