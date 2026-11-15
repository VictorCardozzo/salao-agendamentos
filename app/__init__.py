from flask import Flask, request, jsonify, render_template
from app.models import db, Agendamento, HORARIOS_PERMITIDOS

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salao.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET"])
    def index():
        agendamentos = Agendamento.query.order_by(Agendamento.horario).all()
        ocupados = {a.horario for a in agendamentos}
        return render_template(
            "index.html",
            agendamentos=agendamentos,
            horarios=HORARIOS_PERMITIDOS,
            ocupados=ocupados
        )

    @app.route("/agendamentos", methods=["POST"])
    def criar_agendamento():
        dados = request.get_json() or {}
        horario_solicitado = dados.get("horario", "").strip()

        # Check de conflito no banco de dados
        if Agendamento.query.filter_by(horario=horario_solicitado).first():
            return jsonify({"erro": "Este horário já está ocupado. Escolha outro."}), 409

        try:
            novo = Agendamento(
                cliente_nome=dados.get("cliente_nome", ""),
                servico=dados.get("servico", ""),
                horario=horario_solicitado
            )
            db.session.add(novo)
            db.session.commit()
            return jsonify({"id": novo.id, "cliente": novo.cliente_nome}), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @app.route("/agendamentos", methods=["GET"])
    def listar_agendamentos():
        lista = Agendamento.query.order_by(Agendamento.horario).all()
        return jsonify([
            {"id": a.id, "cliente": a.cliente_nome, "servico": a.servico, "horario": a.horario}
            for a in lista
        ]), 200

    return app