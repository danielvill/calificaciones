from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.tareas import Tarea
from pymongo import MongoClient
db = dbase()

tareas = Blueprint('tareas', __name__)

# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'resultadoId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

@tareas.route("/admin/in_tarea", methods=['GET', 'POST'])
def adtarea():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('resultado.index')) 
    estudiante = db['estudiante'].find()
    materia = db['materia'].find()
    profesor = db['profesor'].find()
    if request.method == 'POST':
        id_resultado = str(get_next_sequence('resultadoId')).zfill(1)
        resultado = db['tareas']
        
        cedula = request.form['cedula']# Este tiene que ser la cedula del estudiante
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        deber = request.form['deber']
        materias = request.form['materias']
        bimestre = request.form ["bimestre"]
        profesor = request.form["profesor"]
        nota = request.form['nota']

        resultado.insert_one(Tarea(id_resultado, cedula, nombre, apellido,paralelo,n_año,deber, materias, bimestre,profesor,nota).TareadoDBCollection())
        flash("Calificacion ingresada exitosamente","success")
        return redirect(url_for('tareas.transicion'))
    else:
        return render_template("admin/in_tarea.html",estudiante = estudiante ,materia = materia , profesor = profesor)
    
# Animacion para transicion
@tareas.route('/ad_tarea')
def transicion():
    return render_template('transi/ad_tarea.html')

@tareas.route('/tareas/adtarea')
def adtar():
    return redirect(url_for('tareas.adtarea'))

# * Editar Resultado
@tareas.route('/edit_ta/<string:edire>', methods=['GET', 'POST'])
def edit_ta(edire):
    tarea = db["tareas"]
    cedula = request.form["cedula"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    paralelo = request.form["paralelo"]
    n_año = request.form["n_año"]
    deber = request.form["deber"]
    materias = request.form["materias"]
    bimestre = request.form ["bimestre"]
    nota = request.form["nota"]

    if cedula  and nombre and apellido and paralelo  and n_año  and deber and materias and bimestre  and nota:
        tarea.update_one ({"id_resultado":edire},{"$set":{"cedula":cedula,"nombre":nombre ,"apellido":apellido , "paralelo":paralelo, "n_año":n_año,  "deber":deber, "materias":materias, "bimestre":bimestre,"nota":nota}})
        flash("Editado correctamente " ,"success")
        return redirect(url_for('tareas.v_tarea'))
    else:
        return render_template('admin/tarea.html')

# * Eliminar Tareas
@tareas.route('/delete_ta/<string:elita>')
def delete_ta(elita):
    tarea = db["tareas"]
    documento =  tarea.find_one({"id_resultado":elita})
    nombre = documento["nombre"]
    apellido = documento["apellido"]
    tarea.delete_one({"id_resultado":elita})
    flash("Estudiante " + nombre + " "+ apellido  +  " eliminado correctamente" ,"success") 
    return redirect(url_for('tareas.v_tarea'))


# Visualizar tareas
@tareas.route("/admin/tarea")
def v_tarea():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('tareas.index'))
    tareas = db['tareas'].find()
    materia = db['materia'].find()
    return render_template("admin/tarea.html", tareas=tareas,materia = materia)
