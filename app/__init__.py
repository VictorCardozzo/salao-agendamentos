from datetime import date
from flask import Flask, request, jsonify, render_template
from app.models import db, Agendamento, obter_horarios_por_data, proxima_data_util

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
        data_padrao = proxima_data_util(date.today()).isoformat()
        data_selecionada = request.args.get("data") or data_padrao

        try:
            data_obj = date.fromisoformat(data_selecionada)
        except ValueError:
            data_selecionada = data_padrao
            data_obj = date.fromisoformat(data_selecionada)

        is_domingo = data_obj.weekday() == 6
        is_sabado = data_obj.weekday() == 5
        horarios_do_dia = obter_horarios_por_data(data_obj)

        agendamentos = (
            Agendamento.query.filter_by(data=data_selecionada)
            .order_by(Agendamento.horario)
            .all()
        )
        ocupados = {a.horario for a in agendamentos}

        return render_template(
            "index.html",
            agendamentos=agendamentos,
            horarios=horarios_do_dia,
            ocupados=ocupados,
            data_selecionada=data_selecionada,
            hoje=date.today().isoformat(),
            is_domingo=is_domingo,
            is_sabado=is_sabado,
        )

    @app.route("/agendamentos", methods=["POST"])
    def criar_agendamento():
        dados = request.get_json() or {}
        data_solicitada = (dados.get("data") or proxima_data_util(date.today()).isoformat()).strip()
        horario_solicitado = dados.get("horario", "").strip()

        if Agendamento.query.filter_by(data=data_solicitada, horario=horario_solicitado).first():
            return jsonify({"erro": "Este horário já está ocupado nesta data."}), 409

        try:
            novo = Agendamento(
                cliente_nome=dados.get("cliente_nome", ""),
                servico=dados.get("servico", ""),
                horario=horario_solicitado,
                data=data_solicitada,
            )
            db.session.add(novo)
            db.session.commit()
            return jsonify({
                "id": novo.id,
                "cliente": novo.cliente_nome,
                "data": novo.data,
                "horario": novo.horario,
            }), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @app.route("/agendamentos", methods=["GET"])
    def listar_agendamentos():
        data_filtro = request.args.get("data")
        query = Agendamento.query
        if data_filtro:
            query = query.filter_by(data=data_filtro)
        lista = query.order_by(Agendamento.data, Agendamento.horario).all()
        return jsonify([
            {
                "id": a.id,
                "cliente": a.cliente_nome,
                "servico": a.servico,
                "data": a.data,
                "horario": a.horario,
            }
            for a in lista
        ]), 200

    return app