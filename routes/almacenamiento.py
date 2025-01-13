from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.almacenamiento import Almacenamiento
from pymongo import MongoClient
db = dbase()

almacenamiento = Blueprint('almacenamiento', __name__)





# Visualizar almacenamiento
@almacenamiento.route("/admin/almacenamiento")
def v_almacenamiento():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('almacenamiento.index'))
    almacenamiento = db['almacenamiento'].find()
    return render_template("admin/almacenamiento.html", almacenamiento=almacenamiento)

