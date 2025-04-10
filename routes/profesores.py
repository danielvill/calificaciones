from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.profesores import Profesores
from modules.resultado import Resultado
from modules.tareas import Tarea
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
        cedula = request.form['cedula']
        clave = request.form['clave']

        profi = Profesores(id_profe,nombre,n_materia,cursos,año,cedula,clave)
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
    cedula = request.form["cedula"]
    
    if nombre and  n_materia and cursos and año and cedula :
        profesor.update_one({'id_profe' : edpro}, {'$set' : { "nombre":nombre  , "n_materia":n_materia ,"cursos": cursos ,"año": año ,  "cedula" :cedula }})
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


# Este es apartado de los Profesores todo el codigo que pertenesca a ellos sera procesado aqui

@profesores.route("/profesor/estudiantes", methods=['GET', 'POST'])
def v_proestudi():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    estudiantes = db['estudiante'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })
    
    return render_template("profesor/estudiantes.html", estudiantes=estudiantes)


# Ingreso de tareas e ingreso de examenes 
# Este codigo es para lo que es el ID tareas
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

@profesores.route("/profesor/in_calificacion", methods=['GET', 'POST'])
def adprota():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('resultado.index')) 
    
    
    # Obtener la información del profesor que ha iniciado sesión
    
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Para obtener la sesion del profesor que ingreso
    nombre_profesor = profesor['nombre']
    # Este para obtener la materia del profesor
    nombre_materia = profesor['n_materia']


    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    estudiantes = db['estudiante'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })


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
        return redirect(url_for('profesores.transicion2'))
    else:
        return render_template("profesor/in_calificacion.html",materi = nombre_materia ,usuario=nombre_profesor,estudiantes = estudiantes ,materia = materia , profesor = profesor)

# Animacion para transicion
@profesores.route('/profe')
def transicion2():
    return render_template('transi/profe.html')

@profesores.route('/profesores/adprota')
def prota():
    return redirect(url_for('profesores.adprota'))


# Visualizar los trabajos de los alumnos del profesor
@profesores.route("/profesor/calificacion")
def profetarea():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    tareas = db['tareas'].find(
        {
            'n_año': profesor['cursos'], 
            'paralelo': profesor['año']
        }
    )
    materia = db['materia'].find(
        {
            'n_año': profesor['cursos'], 
            'paralelo': profesor['año']
        }
    )
    return render_template("profesor/calificacion.html", tareas=tareas,materia = materia)


# Parte del codigo que necesito para agregar examen

# Este codigo es para lo que es el ID para examen
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'examenId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

@profesores.route("/profesor/in_examen", methods=['GET', 'POST'])
def proexa():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index')) 
    # Obtener la información del profesor que ha iniciado sesión
    
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Para obtener la sesion del profesor que ingreso
    nombre_profesor = profesor['nombre']
    # Este para obtener la materia del profesor
    nombre_materia = profesor['n_materia']


    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    estudiantes = db['estudiante'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })

    materia = db['materia'].find()
    profesor = db['profesor'].find()
    
    if request.method == 'POST':
        id_resultado = str(get_next_sequence('examenId')).zfill(1)
        resultado = db['resultado']
        
        cedula = request.form['cedula']# Este tiene que ser la cedula del estudiante
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        fecha_creacion = request.form['fecha_creacion']
        materias = request.form['materias']
        bimestre = request.form ["bimestre"]
        profesor = request.form["profesor"]
        nota = request.form['nota']

        exist_materias = resultado.find_one ({"materias":materias,"nombre":nombre,"apellido":apellido,"bimestre":bimestre })
        if exist_materias:
            flash("Esa materia o ese bimestre con ese nombre y apellido ya ha sido registrada" ,"danger") 
            return redirect(url_for('resultado.adresultado'))
        else:
            resultado.insert_one(Resultado(id_resultado, cedula, nombre, apellido,paralelo,n_año,fecha_creacion, materias, bimestre,profesor,nota).ResultadoDBCollection())
            flash("Calificacion ingresada exitosamente","success")
            return redirect(url_for('profesores.transicion3'))
    else:
        return render_template("profesor/in_examen.html",materi = nombre_materia ,usuario=nombre_profesor,estudiantes = estudiantes ,materia = materia , profesor = profesor)

# Animacion para transicion de examenes
@profesores.route('/profetas')
def transicion3():
    return render_template('transi/profetas.html')

@profesores.route('/profesores/proexa')
def examen():
    return redirect(url_for('profesores.proexa'))




# Mostrar los estudiantes

@profesores.route("/profesor/examen")
def v_examen():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    resultado = db['resultado'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })
    
    materia = db['materia'].find(
        {
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    }
    )
    
    return render_template("profesor/examen.html", resultado=resultado,materia = materia)


# Editar calificaciones 
@profesores.route('/edit_procali/<string:edcal>', methods=['GET', 'POST'])#
def edit_procali(edcal):
    resultado = db['resultado']
    cedula = request.form["cedula"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    n_año = request.form["n_año"]
    deber = request.form["deber"]
    materias = request.form["materias"]
    bimestre = request.form ["bimestre"]
    nota = request.form["nota"]
    if  cedula and nombre and apellido and n_año and deber and materias and bimestre  and nota:
        resultado.update_one({'id_resultado' : edcal}, {'$set' : { "cedula":cedula,"nombre":nombre ,"apellido":apellido , "n_año":n_año,  "deber":deber, "materias":materias, "bimestre":bimestre,"nota":nota}})
        flash("Calificacion editada correctamente " ,"success")
        return redirect(url_for('profesores.profetarea'))
    else:
        return render_template('profesor/calificacion.html')

# Editar Examen
@profesores.route('/edit_proexa/<string:edexa>', methods=['GET', 'POST'])#
def edit_proexa(edexa):
    tarea = db['tarea']
    
    nota = request.form["nota"]
    if nota:
        tarea.update_one({'id_resultado' : edexa}, {'$set' : { "nota":nota }})
        flash("Examen editado correctamente " ,"success")
        return redirect(url_for('profesores.v_examen'))
    else:
        return render_template('profesor/examen.html')