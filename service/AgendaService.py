from models.agenda import Agenda
from models.meGusta import meGusta
from repository.meGustaRepository import meGustaRepository

class AgendaService:
    def __init__(self, meGustarepository, agendaRepository):
        self.megustaRepository = meGustarepository
        self.agendaRepository = agendaRepository

    def generar_agenda(usuarioID, viajeID):
        meGustas = meGustaRepository.buscarGustas(usuarioID, viajeID)
        hora = 14.0
        con = 1
        agenda = {}
        horas = {(9.0,11.0), (12.0,15.0), (17.0,19.0), (21.0,23.0)}

        #recorre las horas de un dia
        while hora <= 23.0:
            for m in meGustas: #recorre la lista de me gusta
                if m.tipo == 'restaurant':
                    if horas.containst(hora):
                        if con not in agenda:
                            agenda[con] = {} #inicializa el indice del dia
                        agenda[con][(hora, hora + m.duracion)] = m.id

                if m.horaInicio < hora < m.horaFin: #si en ese momento esta abierto se agrega a la lista
                    if con not in agenda:
                        agenda[con] = {} #inicializa el indice del dia
                    agenda[con][(hora, hora + m.duracion)] = m.id
                hora += m.duracion + 0.5
            
            con += 1
        return agenda

#agenda = {
#    1: {
#        (14, 16): "ir a la playa",
#        (16.5, 18.5): "ir a comer a tal lugar"
#    },
#    2: {},
#    3: {}
#}
