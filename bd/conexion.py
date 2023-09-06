from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def getEngine():
    database_url = 'postgresql://sofia:clavesofiaIF012@if012atur.fi.mdn.unp.edu.ar:28001/if012'
    engine = create_engine(database_url, echo=True)
    return engine

def getSession():
    return sessionmaker(bind=getEngine())
