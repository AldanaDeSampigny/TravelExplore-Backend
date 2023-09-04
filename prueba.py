import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = 'postgresql://sofia:clavesofiaIF012@if012atur.fi.mdn.unp.edu.ar:28001/if012'

engine = create_engine(database_url, echo=True)
#sessionmaker(bind=engine)

metadata_obj = db.MetaData()
  
# Define the profile table
  
# database name
profile = db.Table(
    'profile',                                        
    metadata_obj,                                    
    db.Column('email', db.String, primary_key=True),  
    db.Column('name', db.String),                    
    db.Column('contact', db.Integer),                
)
  
# Create the profile table
metadata_obj.create_all(engine)