class Agendamento:
    def __init__(self, cliente_nome: str, servico: str, horario: str):
        if not cliente_nome or len(cliente_nome.strip()) < 2:
            raise ValueError("Nome do cliente inválido.")
        self.cliente_nome = cliente_nome.strip()
        self.servico = servico
        self.horario = horario