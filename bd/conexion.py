from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def getEngine():
    database_url = 'postgresql://sofia:clavesofiaIF012@if012atur.fi.mdn.unp.edu.ar:28001/if012'
    engine = create_engine(database_url, echo=False)
    return engine

def getSession():
    return sessionmaker(bind=getEngine())