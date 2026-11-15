from flask import Flask, request, jsonify
from app.models import db, Agendamento

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salao.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/agendamentos", methods=["POST"])
    def criar_agendamento():
        dados = request.get_json() or {}
        try:
            novo = Agendamento(
                cliente_nome=dados.get("cliente_nome", ""),
                servico=dados.get("servico", ""),
                horario=dados.get("horario", "")
            )
            db.session.add(novo)
            db.session.commit()
            return jsonify({"id": novo.id, "cliente": novo.cliente_nome}), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @app.route("/agendamentos", methods=["GET"])
    def listar_agendamentos():
        lista = Agendamento.query.all()
        return jsonify([
            {"id": a.id, "cliente": a.cliente_nome, "servico": a.servico, "horario": a.horario}
            for a in lista
        ]), 200

    return app