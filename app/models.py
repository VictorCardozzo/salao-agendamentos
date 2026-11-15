from datetime import date, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

HORARIOS_SEMANA = [
    "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00",
    "18:00", "19:00", "20:00"
]

HORARIOS_SABADO = [
    "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00"
]

def obter_horarios_por_data(data_obj: date) -> list[str]:
    dia_semana = data_obj.weekday()  # 0=Seg ... 5=Sáb, 6=Dom
    if dia_semana == 6:
        return []
    if dia_semana == 5:
        return HORARIOS_SABADO
    return HORARIOS_SEMANA

def proxima_data_util(data_obj: date) -> date:
    if data_obj.weekday() == 6:
        return data_obj + timedelta(days=1)
    return data_obj

class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    __table_args__ = (
        db.UniqueConstraint("data", "horario", name="uix_data_horario"),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    horario = db.Column(db.String(20), nullable=False)

    def __init__(self, cliente_nome: str, servico: str, horario: str, data: str = None):
        if not cliente_nome or len(cliente_nome.strip()) < 2:
            raise ValueError("Nome do cliente inválido.")
        if not servico or not horario:
            raise ValueError("Serviço e horário são obrigatórios.")

        data_limpa = (data or proxima_data_util(date.today()).isoformat()).strip()
        try:
            data_obj = date.fromisoformat(data_limpa)
        except ValueError:
            raise ValueError("Data inválida. Utilize o formato AAAA-MM-DD.")

        if data_obj.weekday() == 6:
            raise ValueError("O salão não funciona aos domingos.")

        horarios_validos = obter_horarios_por_data(data_obj)
        horario_limpo = horario.strip()
        if horario_limpo not in horarios_validos:
            if data_obj.weekday() == 5:
                raise ValueError("Aos sábados, o atendimento é apenas de 09:00 às 16:00.")
            raise ValueError("Horário fora do expediente (08:00 às 20:00).")

        self.cliente_nome = cliente_nome.strip()
        self.servico = servico.strip()
        self.data = data_limpa
        self.horario = horario_limpo