from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.profesores import Profesores
from pymongo import MongoClient
db = dbase()

profesores = Blueprint('profesores', __name__)

# Este codigo es para lo que es el ID
# id_profe n_materia  cursos  año  fecha_creacion

def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'profeId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

# Ingresar profesores
@profesores.route("/admin/in_profesor", methods=['GET', 'POST'])
def adpro():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesor.index')) 
    materia = db["materia"].find()
    if request.method == 'POST':
        id_profe = str(get_next_sequence('profeId')).zfill(1)
        profesor = db['profesor']
        nombre = request.form['nombre']
        n_materia = request.form['n_materia']
        cursos = request.form['cursos']
        año = request.form['año']
        fecha_creacion = request.form['fecha_creacion']

        profi = Profesores(id_profe,nombre,n_materia,cursos,año,fecha_creacion)
        profesor.insert_one(profi.ProfesorDBCollection())
        flash("Profesor Ingresado exitosamente" ,"success")
        return redirect(url_for('profesores.transicion'))
    else:
        return render_template("admin/in_profesor.html",materia=materia)


# Animacion para transicion
@profesores.route('/ad_profe')
def transicion():
    return render_template('transi/ad_profe.html')

@profesores.route('/profesores/adpro')
def adprofe():
    return redirect(url_for('profesores.adpro'))


# id_profe n_materia  cursos  año  fecha_creacion


# Editar profesores
@profesores.route('/edit_profesor/<string:edpro>', methods=['GET', 'POST'])#
def edit_profesor(edpro):
    profesor = db['profesor']
    nombre = request.form["nombre"]
    n_materia = request.form["n_materia"]
    cursos = request.form['cursos']
    año = request.form["año"]
    fecha_creacion = request.form["fecha_creacion"]
    
    if nombre and  n_materia and cursos and año and fecha_creacion :
        profesor.update_one({'id_profe' : edpro}, {'$set' : { "nombre":nombre  , "n_materia":n_materia ,"cursos": cursos ,"año": año ,  "fecha_creacion" :fecha_creacion }})
        flash("Profesor editado correctamente " ,"success")
        return redirect(url_for('profesores.v_profe'))
    else:
        return render_template('admin/profesor.html')


# * Eliminar año
@profesores.route('/delete_profe/<string:elipro>')
def delete_profe(elipro):
    profesor = db["profesor"]
    documento =  profesor.find_one({"id_profe":elipro})
    id_profe = documento["id_profe"]
    profesor.delete_one({"id_profe":elipro})
    flash(  "Codigo " +  id_profe +  " eliminado correctamente" ,"success") 
    return redirect(url_for('profesores.v_profe'))




# Visualizar año
@profesores.route("/admin/profesor")
def v_profe():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    profesor = db['profesor'].find()
    materia = db["materia"].find()
    return render_template("admin/profesor.html", profesor=profesor,materia=materia)
