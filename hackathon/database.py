import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OverlapInfo(Base):
    __tablename__ = 'overlap_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_index = Column(Integer)
    region_id = Column(Integer)
    bbox_minr = Column(Integer)
    bbox_minc = Column(Integer)
    bbox_maxr = Column(Integer)
    bbox_maxc = Column(Integer)
    overlap_image = Column(String)


class NonOverlapInfo(Base):
    __tablename__ = 'non_overlap_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_index = Column(Integer)
    region_id = Column(Integer)
    bbox_minr = Column(Integer)
    bbox_minc = Column(Integer)
    bbox_maxr = Column(Integer)
    bbox_maxc = Column(Integer)
    non_overlap_image = Column(String)


def initialize_database(db_path):
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
