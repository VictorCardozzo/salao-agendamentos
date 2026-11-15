from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(20), nullable=False)

    def __init__(self, cliente_nome: str, servico: str, horario: str):
        if not cliente_nome or len(cliente_nome.strip()) < 2:
            raise ValueError("Nome do cliente inválido.")
        if not servico or not horario:
            raise ValueError("Serviço e horário são obrigatórios.")
        self.cliente_nome = cliente_nome.strip()
        self.servico = servico.strip()
        self.horario = horario.strip()