from flask import Flask, request, make_response, jsonify, render_template
from pony import orm
from datetime import datetime, time, date
from collections import defaultdict
from datetime import datetime
from itertools import groupby
import random

db = orm.Database()

app = Flask(__name__, static_url_path='/static')

class Trening(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    otplivana_daljina = orm.Required(int)
    vrijeme = orm.Required(time)
    datum_tr = orm.Required(date)
    detalji = orm.Required(str)


db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)


def formatiraj_datum(datum):
    return datum.strftime('%d-%m-%Y') if datum else None


def add_trening(json_request):
    try:
        otplivana_daljina = json_request["otplivana_daljina"]
        vrijeme = time.fromisoformat(json_request['vrijeme']) if json_request['vrijeme'] else None
        datum_tr = datetime.fromisoformat(json_request['datum_tr'])
        detalji = json_request["detalji"]

        with orm.db_session:
            Trening(otplivana_daljina=otplivana_daljina, vrijeme=vrijeme, datum_tr=datum_tr, detalji=detalji)
            response = {"response": "Success"}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}



def get_trening():
    try:
        with orm.db_session:
            db_querry = orm.select(x for x in Trening)[:]
            lista_treninga = []
            for t in db_querry:
                lista_treninga.append(t.to_dict())
            response = {"response": "Success", "data": lista_treninga}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


def get_trening_by_month():
    try:
        with orm.db_session:
            db_query = orm.select(x for x in Trening)[:]
            lista_treninga = defaultdict(int)

            for trening in db_query:
                if trening.datum_tr:
                    month = trening.datum_tr.month
                    lista_treninga[month] += 1

            response = {"response": "Success", "data": dict(lista_treninga)}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


@orm.db_session
def get_trening_by_otplivana_daljina():
    try:
        treninzi = orm.select(y for y in Trening).order_by(Trening.otplivana_daljina)
        grouped_by_otplivana_daljina = groupby(treninzi, lambda y: y.otplivana_daljina)
        result = [{"otplivana_daljina": otplivana_daljina, "broj_treinga": len(list(treninzi))} for otplivana_daljina, treninzi in grouped_by_otplivana_daljina]
        response = {"response": "Success", "data": {"kategorije": result}}
        return response
    except Exception as e:
        error_response = {"response": "Error", "error_message": str(e)}
        return error_response


def get_trening_by_id(trening_id):
    try:
        with orm.db_session:
            result = Trening[trening_id].to_dict()
            result['datum_tr'] = formatiraj_datum(result['datum_tr'])
            response = {"response": "Success", "data": result}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


def patch_trening(trening_id, json_request):
    try:
        with orm.db_session:
            to_update = Trening[trening_id]
            if 'otplivana_daljina' in json_request:
                to_update.otplivana_daljina = json_request['otplivana_daljina']
            if 'vrijeme' in json_request:
                to_update.vrijeme = json_request['vrijeme'] if json_request['vrijeme'] else None
            if 'datum_tr' in json_request:
                datum_tr = datetime.strptime(json_request['datum_tr'], '%Y-%m-%d')
                to_update.datum_tr = datum_tr
            if 'detalji' in json_request:
                to_update.detalji = json_request['detalji']
            response = {"response": "Success"}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


def obrisi_trening(trening_id):
    try:
        with orm.db_session:
            to_delete = Trening[trening_id]
            to_delete.delete()
            response = {"response": "Success"}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


@app.route("/dodaj/trening", methods=["POST","GET"])
def unos_trening():
    if request.method == "POST":
        try:
            json_request = {}
            for key,value in request.form.items():
                if value == "":
                    json_request[key] = None
                else:
                    json_request[key] = value
        except Exception as e:
            response = {"response":str(e)}
            return make_response(jsonify(response),400)
        response = add_trening(json_request)
        if response["response"] == "Success":
            return make_response(render_template("unos.html"),200)
        return make_response(jsonify(response),400)
    else:
        return make_response(render_template("unos.html"),200)


@app.route("/pregled/treninge", methods=["GET"])
def pregled_treninge():
    if request.args and 'id' in request.args:
        trening_id = int(request.args.get("id"))
        response = get_trening_by_id(trening_id)
        if response["response"] == "Success":
            return make_response(render_template("pregled.html", data=response["data"]), 200)
        return make_response(jsonify(response), 400)
    response = get_trening()
    if response["response"] == "Success":
        return make_response(render_template("pregled.html", data=response["data"]), 200)
    return make_response(jsonify(response), 400)


@app.route("/trening/graf", methods=["GET"])
def graf():
    try:
        chart_data = get_trening_by_month()
        y_axis = list(chart_data.get("data", {}).values())
        x_axis = list(chart_data.get("data", {}).keys())
        response = {"response": "Success"}
        if response["response"] == "Success":
            return make_response(render_template("graf.html", y_axis=y_axis, x_axis=x_axis), 200)
        return make_response(jsonify(response), 400)
    except Exception as e:
        error_response = {"response": "Error", "error_message": str(e)}
        return make_response(jsonify(error_response), 500)


@app.route("/trening/<int:trening_id>", methods=["DELETE"])
def izbrisi_trening(trening_id):
    response = obrisi_trening(trening_id)
    if response["response"] == "Success":
        return make_response(jsonify(response), 200)
    return make_response(jsonify(response), 400)


@app.route("/trening/uredi/<int:trening_id>", methods=["GET", "POST"])
def uredi_trening(trening_id):
    if request.method == "GET":
        response = get_trening_by_id(trening_id)
        if response["response"] == "Success":
            return make_response(render_template("ureditrening.html", data=response["data"]), 200)
        return make_response(jsonify(response), 400)

    if request.method == "POST":
        try:
            json_request = {}
            for key, value in request.form.items():
                if value == "":
                    json_request[key] = None
                else:
                    json_request[key] = value

            response = patch_trening(trening_id, json_request)
            if response["response"] == "Success":
                return make_response(render_template("success.html", message="Trening successfully updated"), 200)
            return make_response(jsonify(response), 400)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 400)


@app.route("/", methods=["GET"])
def home():
    return make_response(render_template("website.html"), 200)

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True)

