from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.estudiante import Estudiante
from pymongo import MongoClient
db = dbase()
estudiante = Blueprint('estudiante', __name__)


# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'estudianteId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')


# Ingresar Estudiante
@estudiante.route("/admin/in_estudiante", methods=['GET', 'POST'])
def adestudiante():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('estudiante.index'))
    
    
    if request.method == 'POST':
        id_estudiante = str(get_next_sequence('estudianteId')).zfill(1)
        estudiante = db['estudiante']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        clave = request.form['clave']

        exist_cedula = estudiante.find_one ({"cedula":cedula})

        if exist_cedula:
            flash("Ya existe esa cedula","danger")
            return redirect(url_for('estudiante.adestudiante'))
        
        else:
            estudiante.insert_one(Estudiante(id_estudiante, nombre, apellido, cedula, paralelo, n_año, clave).EstudianteDBCollection())
            flash("Estudiante ingresado exitosamente","success")
            return redirect(url_for('estudiante.transicion'))
    else:
        return render_template("admin/in_estudiante.html" )
# Animacion para transicion
@estudiante.route('/transi')
def transicion():
    return render_template('transi/ad_estu.html')

@estudiante.route('/estudiante/adestudiante')
def ade():
    return redirect(url_for('estudiante.adestudiante'))


# * Editar Estudiante
@estudiante.route('/edit_es/<string:edies>', methods=['GET', 'POST'])
def edit_es(edies):
    estudiante = db["estudiante"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    cedula = request.form["cedula"]
    paralelo = request.form["paralelo"]
    n_año = request.form["n_año"]
    clave = request.form["clave"]

    if nombre and apellido and cedula and paralelo and n_año and clave:
        estudiante.update_one({"id_estudiante": edies}, {"$set": {"nombre": nombre, "apellido": apellido, "cedula": cedula, "paralelo": paralelo, "n_año": n_año, "clave": clave}})
        flash("Estudiante editado correctamente" ,"success")
        return redirect(url_for('estudiante.v_estudiante'))
    else:
        return render_template("admin/in_estudiante.html")



# * Eliminar Estudiante
@estudiante.route('/delete_es/<string:elies>')
def delete_es(elies):
    estudiante = db["estudiante"]
    documento =  estudiante.find_one({"id_estudiante":elies})
    nombre = documento["nombre"]
    apellido = documento["apellido"]
    estudiante.delete_one({"id_estudiante":elies})
    flash("Estudiante " + nombre + " "+ apellido  +  " eliminado correctamente" ,"success") 
    return redirect(url_for('estudiante.v_estudiante'))



# * Visualizar Estudiante
@estudiante.route("/admin/estudiante")
def v_estudiante():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('estudiante.index'))
    estudiante = db['estudiante'].find()
    return render_template("admin/estudiante.html", estudiante=estudiante)

