from bd.conexion import getSession
from models.meGusta import meGusta

class gustaPresenter:
    def __init__(self):
        self.session = getSession()

    def get_activities(self):
        activities = self.session.query(meGusta).all()
        return activities

    def get_activity_by_id(self, activity_id):
        activity = self.session.query(meGusta).filter_by(id=activity_id).first()
        return activity