from datetime import date
import pytest
from app import create_app
from app.models import Agendamento, proxima_data_util

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client:
        yield client

# --- TESTES UNITÁRIOS ---
def test_unitario_criar_modelo_valido_semana():
    ag = Agendamento("  Maria Silva  ", "Corte", "19:00", "2026-11-20")  # Sexta-feira
    assert ag.cliente_nome == "Maria Silva"
    assert ag.servico == "Corte"
    assert ag.horario == "19:00"
    assert ag.data == "2026-11-20"

def test_unitario_criar_modelo_valido_sabado():
    ag = Agendamento("Carla", "Escova", "16:00", "2026-11-21")  # Sábado
    assert ag.horario == "16:00"

def test_unitario_sabado_fora_horario_dispara_erro():
    with pytest.raises(ValueError, match="sábados"):
        Agendamento("Carla", "Corte", "08:00", "2026-11-21")
    with pytest.raises(ValueError, match="sábados"):
        Agendamento("Carla", "Corte", "17:00", "2026-11-21")

def test_unitario_domingo_dispara_erro():
    with pytest.raises(ValueError, match="domingos"):
        Agendamento("Carla", "Corte", "10:00", "2026-11-22")  # Domingo

def test_unitario_proxima_data_util_pula_domingo():
    domingo = date(2026, 11, 22)
    segunda = date(2026, 11, 23)
    assert proxima_data_util(domingo) == segunda
    assert proxima_data_util(segunda) == segunda

def test_unitario_nome_invalido_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("A", "Corte", "14:00", "2026-11-20")

def test_unitario_campos_vazios_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("Maria", "", "", "2026-11-20")

def test_unitario_data_invalida_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("Maria", "Corte", "14:00", "20-11-2026")

def test_unitario_horario_fora_expediente_semana_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("Maria", "Corte", "22:00", "2026-11-20")

# --- TESTES DE INTEGRAÇÃO ---
def test_integracao_index_carrega_semana_sabado_e_domingo(client):
    resp_sex = client.get("/?data=2026-11-20")
    assert resp_sex.status_code == 200
    assert b"08:00" in resp_sex.data

    resp_sab = client.get("/?data=2026-11-21")
    assert resp_sab.status_code == 200
    assert b"09:00" in resp_sab.data
    assert b"08:00" not in resp_sab.data

    resp_dom = client.get("/?data=2026-11-22")
    assert resp_dom.status_code == 200
    assert b"fechado aos domingos" in resp_dom.data

    resp_invalida = client.get("/?data=invalida")
    assert resp_invalida.status_code == 200

def test_integracao_criar_e_listar_por_data(client):
    resp_post = client.post("/agendamentos", json={
        "cliente_nome": "Ana",
        "servico": "Escova",
        "horario": "15:00",
        "data": "2026-11-20"
    })
    assert resp_post.status_code == 201

    resp_get = client.get("/agendamentos?data=2026-11-20")
    assert resp_get.status_code == 200
    assert len(resp_get.get_json()) == 1

def test_integracao_bloqueia_domingo_e_horario_duplicado(client):
    resp_dom = client.post("/agendamentos", json={"cliente_nome": "Ana", "servico": "Corte", "horario": "10:00", "data": "2026-11-22"})
    assert resp_dom.status_code == 400

    client.post("/agendamentos", json={"cliente_nome": "Ana", "servico": "Corte", "horario": "10:00", "data": "2026-11-20"})
    resp_dup = client.post("/agendamentos", json={"cliente_nome": "Bia", "servico": "Unha", "horario": "10:00", "data": "2026-11-20"})
    assert resp_dup.status_code == 409