from ..bd.conexion import getEngine
from ..models.MeGustas import MeGustas
from sqlalchemy.orm import Session

class GustaService:
    def __init__(self):
        pass

    def get_activities(self):
        with Session(getEngine()) as session:
            activities = session.query(MeGustas).all()
            return activities

    def get_activity_by_id(self, activity_id):
        with Session(getEngine()) as session:
            activity = session.query(MeGustas).filter_by(id=activity_id).first()
            return activity