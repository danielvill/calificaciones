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

# Ingresar Materia
@materia.route("/admin/in_materia", methods=['GET', 'POST'])
def admateria():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('materia.index'))
    if request.method == 'POST':
        id_materia = str(get_next_sequence('materiaId')).zfill(1)
        materia = db['materia']
        n_materia = request.form['n_materia']
        fecha_creacion = request.form['fecha_creacion']
        
        exist_materia = materia.find_one ({"n_materia":n_materia})

        if exist_materia:
            flash("Ya existe esa materia","danger")
            return redirect(url_for('materia.admateria')) 
        else:
            materia.insert_one(Materia(id_materia, n_materia, fecha_creacion).MateriaDBCollection())
            flash("Materia ingresada exitosamente" ,"success")
            return redirect(url_for('materia.transicion'))
    else:
        return render_template("admin/in_materia.html")

# Animacion para transicion
@materia.route('/ad_materia')# Recuerda que debes este nombre
def transicion():
    return render_template('transi/ad_materia.html')

@materia.route('/materia/admateria')
def adma():
    return redirect(url_for('materia.admateria'))




# Editar Materia
@materia.route('/edit_ma/<string:edmate>', methods=['GET', 'POST'])
def edit_ma(edmate):
    materia = db['materia']
    n_materia = request.form['n_materia']
    fecha_creacion = request.form['fecha_creacion']
    
    if n_materia and fecha_creacion :
        materia.update_one({'id_materia' : edmate}, {'$set' : {'n_materia' : n_materia, 'fecha_creacion' : fecha_creacion }})
        flash("Editado correctamente ", "success")
        return redirect(url_for('materia.v_materia'))
    else:
        return render_template('admin/materia.html')



# Eliminar Materia
@materia.route('/delete_materia/<string:elmate>', methods=['GET', 'POST'])
def delete_ma(elmate):
    materia = db['materia']
    documento = materia.find_one({"id_materia":elmate})
    n_materia = documento['n_materia']
    materia.delete_one({"id_materia":elmate})
    flash("Materia "+ n_materia + " eliminada exitosamente", "success")
    return redirect(url_for('materia.v_materia'))



# Visualizar materia
@materia.route("/admin/materia")
def v_materia():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('materia.index'))
    materia = db['materia'].find()
    return render_template("admin/materia.html", materia=materia)

