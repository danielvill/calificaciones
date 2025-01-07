from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.año import Año
from pymongo import MongoClient
db = dbase()

año = Blueprint('año', __name__)

# Visualizar cliente
@año.route("/admin/año")
def v_año():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('año.index'))
    año = db['año'].find()
    return render_template("admin/año.html", año=año)
