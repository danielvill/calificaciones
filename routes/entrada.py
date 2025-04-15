from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.entrada import Entrada
from pymongo import MongoClient
db = dbase()
entrada = Blueprint('entrada', __name__)

# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'entradaId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

# Ingresar año lectivo
@entrada.route("/profesor/in_entrada", methods=['GET', 'POST'])
def proen():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('entrada.index')) 

    usuario = session['username']
    
    # Consultar la base de datos para obtener el profesor con la cédula ingresada
    profesor = db['profesor'].find_one({'cedula': usuario})

    if request.method == 'POST':
        id_entrada = str(get_next_sequence('entradaId')).zfill(1)
        entrada = db['entrada']
        nombre = profesor['nombre'] if profesor else "No encontrado"  # Tomar el nombre del profesor
        cedula = request.form['cedula']
        fecha = request.form['fecha']
        hora = request.form['hora']

        entri = Entrada(id_entrada, nombre, cedula, fecha, hora)
        entrada.insert_one(entri.EntradaDBCollection())

        flash("Entrada ingresada exitosamente", "success")
        return redirect(url_for('entrada.transicion'))
        
    else:
        return render_template("profesor/in_entrada.html", usuario=usuario, profesor=profesor)

# Animacion para transicion
@entrada.route('/proen')
def transicion():
    return render_template('transi/proen.html')

@entrada.route('/entrada/proen')
def proin():
    return redirect(url_for('entrada.proen'))


# Visualizar entrada
@entrada.route("/admin/entrada")
def v_entrada():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('entrada.index'))
    entrada = db['entrada'].find()
    return render_template("admin/entrada.html", entrada=entrada)

