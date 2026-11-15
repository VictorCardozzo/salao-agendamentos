from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

HORARIOS_PERMITIDOS = [
    "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00",
    "18:00", "19:00", "20:00"
]

class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, cliente_nome: str, servico: str, horario: str):
        if not cliente_nome or len(cliente_nome.strip()) < 2:
            raise ValueError("Nome do cliente inválido.")
        if not servico or not horario:
            raise ValueError("Serviço e horário são obrigatórios.")
        
        horario_limpo = horario.strip()
        if horario_limpo not in HORARIOS_PERMITIDOS:
            raise ValueError("Horário fora do expediente (08:00 às 20:00).")

        self.cliente_nome = cliente_nome.strip()
        self.servico = servico.strip()
        self.horario = horario_limpo