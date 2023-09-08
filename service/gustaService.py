from ..bd.conexion import getEngine
from ..models.meGusta import meGustas
from sqlalchemy.orm import Session

class gustaService:
    def __init__(self):
        pass

    def get_activities(self):
        with Session(getEngine()) as session:
            activities = session.query(meGustas).all()
            return activities

    def get_activity_by_id(self, activity_id):
        with Session(getEngine()) as session:
            activity = session.query(meGustas).filter_by(id=activity_id).first()
            return activity