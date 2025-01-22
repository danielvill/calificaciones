from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.año import Año
from pymongo import MongoClient
db = dbase()

año = Blueprint('año', __name__)



# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'añoId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

# Ingresar año lectivo
@año.route("/admin/in_año", methods=['GET', 'POST'])
def adaño():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('año.index')) 
    if request.method == 'POST':
        id_año = str(get_next_sequence('añoId')).zfill(1)
        año = db['año']
        n_año = request.form['n_año']
        paralelo = request.form['paralelo']
        fecha_creacion = request.form['fecha_creacion']

        añi = Año(  id_año ,  n_año, paralelo, fecha_creacion)
        año.insert_one(añi.AñoDBCollection())
        flash("Año ingresado exitosamente" ,"success")
        return redirect(url_for('año.transicion'))
        
    else:
        return render_template("admin/in_año.html")

# Animacion para transicion
@año.route('/transicion')
def transicion():
    return render_template('admin/transicion.html')

@año.route('/año/adaño')
def adñ():
    return redirect(url_for('año.adaño'))




# Editar año 
@año.route('/edit_año/<string:edad>', methods=['GET', 'POST'])#
def edit_año(edad):
    año = db['año']
    n_año = request.form["n_año"]
    
    paralelo = request.form['paralelo']
    fecha_creacion = request.form["fecha_creacion"]
    
    if n_año   and paralelo and fecha_creacion :
        año.update_one({'id_año' : edad}, {'$set' : {'n_año' : n_año, 'paralelo' : paralelo ,"fecha_creacion" :fecha_creacion }})
        flash("Editado correctamente " ,"success")
        return redirect(url_for('año.v_año'))
    else:
        return render_template('admin/año.html')


# * Eliminar año
@año.route('/delete_año/<string:eliad>')
def delete_año(eliad):
    año = db["año"]
    documento =  año.find_one({"id_año":eliad})
    n_año = documento["n_año"]
    año.delete_one({"id_año":eliad})
    flash(  n_año +  " eliminado correctamente" ,"success") 
    return redirect(url_for('año.v_año'))




# Visualizar año
@año.route("/admin/año")
def v_año():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('año.index'))
    año = db['año'].find()
    return render_template("admin/año.html", año=año)
