class AgendaValidaciones:
    def __init__(self, db_session):
        self.db_session = db_session

    def validacionFecha(self, fechaInicio, fechaFin):

        if fechaInicio is None or fechaFin is None:
            raise ValueError("se deben ingresar ambas fechas")

        if fechaInicio >= fechaFin:
            raise ValueError("La fecha de inicio no puede ser mayor o igual que la fecha de fin")
    

    def validacionHora(self, horaInicio, horaFin):

        if horaInicio is None or horaFin is None:
            raise ValueError("se deben ingresar ambos horarios")
        
        if horaInicio >= horaFin:
            raise ValueError("La hora de inicio no puede ser mayor o igual que la hora de fin de actividades")