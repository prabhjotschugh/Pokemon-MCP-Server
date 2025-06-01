from sqlalchemy import Column, Integer, String, Float, JSON
from .database import Base

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    types = Column(JSON)  # Store as JSON array
    stats = Column(JSON)  # Store as JSON object
    abilities = Column(JSON)  # Store as JSON array
    moves = Column(JSON)  # Store as JSON array
    height = Column(Float)
    weight = Column(Float)
    sprite_url = Column(String)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    pokemon_ids = Column(JSON)  # Store as JSON array
    created_at = Column(String)  # Store timestamp 