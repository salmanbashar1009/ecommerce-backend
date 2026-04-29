import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Text, DateTime, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

Base = declarative_base()

class user(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid = True),primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True,) #nullable for social login
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(Enum('admin', 'customer', name = 'user_roles'), default = 'customer')
    is_verified = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships