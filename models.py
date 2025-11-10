from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    # Relationships
    gifter_pairings = relationship("Pairing", foreign_keys="Pairing.gifter_id", back_populates="gifter")
    receiver_pairings = relationship("Pairing", foreign_keys="Pairing.receiver_id", back_populates="receiver")


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)


class Pairing(Base):
    __tablename__ = "pairings"

    id = Column(Integer, primary_key=True, index=True)
    gifter_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    gifter = relationship("User", foreign_keys=[gifter_id], back_populates="gifter_pairings")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="receiver_pairings")

