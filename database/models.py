from sqlalchemy import Column, Integer, String, Boolean, Date, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    gender = Column(String)  # 'male' або 'female'
    birth_date = Column(Date)
    registration_date = Column(Date, default=datetime.now().date())
    notifications_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
class UserIdea(Base):
    __tablename__ = 'user_ideas'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    username = Column(String, nullable=True)
    idea_text = Column(String)
    created_at = Column(Date, default=datetime.now().date())

class AdminSettings(Base):
    __tablename__ = 'admin_settings'
    
    id = Column(Integer, primary_key=True)
    quote_text = Column(String, default="Час минає швидше, ніж ми думаємо...")