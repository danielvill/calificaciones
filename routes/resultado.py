from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.resultado import Resultado
from pymongo import MongoClient
db = dbase()

resultado = Blueprint('resultado', __name__)






# Visualizar resultado
@resultado.route("/admin/resultado")
def v_resultado():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('resultado.index'))
    resultado = db['resultado'].find()
    return render_template("admin/resultado.html", resultado=resultado)

