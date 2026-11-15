import pytest
from app import create_app
from app.models import db, Agendamento

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client:
        yield client

# --- TESTES UNITÁRIOS ---
def test_unitario_criar_modelo_valido():
    ag = Agendamento("  Maria Silva  ", "Corte", "14:00")
    assert ag.cliente_nome == "Maria Silva"
    assert ag.servico == "Corte"
    assert ag.horario == "14:00"

def test_unitario_nome_invalido_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("A", "Corte", "14:00")

def test_unitario_campos_vazios_dispara_erro():
    with pytest.raises(ValueError):
        Agendamento("Maria", "", "")

# --- TESTES DE INTEGRAÇÃO ---
def test_integracao_criar_e_listar_agendamento(client):
    resp_post = client.post("/agendamentos", json={
        "cliente_nome": "Ana",
        "servico": "Escova",
        "horario": "15:30"
    })
    assert resp_post.status_code == 201
    assert resp_post.get_json()["cliente"] == "Ana"

    resp_get = client.get("/agendamentos")
    assert resp_get.status_code == 200
    dados = resp_get.get_json()
    assert len(dados) == 1
    assert dados[0]["servico"] == "Escova"

def test_integracao_post_invalido_retorna_400(client):
    resp = client.post("/agendamentos", json={"cliente_nome": "", "servico": "Unha", "horario": "10:00"})
    assert resp.status_code == 400