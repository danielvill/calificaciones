from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.materia import Materia
from pymongo import MongoClient
db = dbase()

materia = Blueprint('materia', __name__)




# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'materiaId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')


# Visualizar materia
@materia.route("/admin/materia")
def v_materia():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('materia.index'))
    materia = db['materia'].find()
    return render_template("admin/materia.html", materia=materia)

