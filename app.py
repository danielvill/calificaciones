from flask import flash, Flask,  make_response,json, send_file,session, render_template, request,Response ,jsonify, redirect, url_for
from bson import json_util
from controllers.database import Conexion as dbase
from datetime import datetime,timedelta #* Importacion de manejo de tiempo
from flask import jsonify
from reportlab.pdfgen import canvas # *pip install reportlab este es para imprimir reportes
from reportlab.lib.pagesizes import letter #* pip install reportlab 
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer ,Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet ,ParagraphStyle
from routes.año import año
from routes.estudiante import estudiante
from routes.materia import materia
from routes.almacenamiento import almacenamiento
from routes.resultado import resultado
from routes.chat import chat_bp
from routes.profesores import profesores
from routes.tareas import tareas
from routes.entrada import entrada
import io
import os
from collections import defaultdict
db = dbase()
app = Flask(__name__)
app.secret_key = 'calificaciones'


# * Crear Backup de la base de datos 
@app.route('/crear_backup', methods=['POST'])
def crear_backup():
    # Obtén los datos de las colecciones 'estudiante', 'stock' y 'usuarios'
    estudiante_data = db.estudiante.find({}, {'_id': 0})  # Excluye el campo '_id'
    profesor_data = db.profesor.find({}, {'_id': 0})
    resultado_data = db.resultado.find({}, {'_id': 0})

    # Crea una carpeta para los respaldos (si no existe)
    backup_folder = 'backups'
    os.makedirs(backup_folder, exist_ok=True)

    # Genera nombres de archivo con la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    estudiante_filename = f'{backup_folder}/estudiante_{fecha_actual}.json'
    profesor_filename = f'{backup_folder}/profesor_{fecha_actual}.json'
    resultado_filename = f'{backup_folder}/resultado_{fecha_actual}.json'

    # Guarda los datos en archivos JSON
    with open(estudiante_filename, 'w') as estudiante_file:
        for empleado in estudiante_data:
            json.dump(empleado, estudiante_file)
            estudiante_file.write('\n')

    with open(profesor_filename, 'w') as profesor_file:
        for herramienta in profesor_data:
            json.dump(herramienta, profesor_file)
            profesor_file.write('\n')

    with open(resultado_filename, 'w') as resultado_file:
        for resultado in resultado_data:
            json.dump(resultado, resultado_file)
            resultado_file.write('\n')
    return redirect(url_for('completo'))

# * Vista de Ingreso al sistema 
# Transiciones
@app.route('/completo')
def completo():
    return render_template('/admin/completo.html')

@app.route('/admin/completo')
def adcomp():
    return redirect(url_for('chat.chat'))

# * Vista de Ingreso al sistema 
@app.route('/',methods=['GET','POST'])
def run():
    return render_template('main.html')


#* Este es para cerrar la sesion 
@app.route('/logout')
def logout():
    # Elimina el usuario de la sesión si está presente
    session.pop('username', None)
    return redirect(url_for('index'))





#* Vista Ingreso de admin y alumnos
@app.route('/index',methods=['GET','POST'])
def index():

    if request.method == 'POST':
        usuario = request.form['cedula']
        password = request.form['clave']
        usuario_fo = db.admin.find_one({'cedula':usuario,'clave':password})
        estudiante = db.estudiante.find_one({'cedula':usuario,'clave':password})
        profesor = db.profesor.find_one({'cedula':usuario,'clave':password})
        if usuario_fo:
            session["username"]= usuario
            return redirect(url_for('año.v_año'))
        elif estudiante:
            session["username"]= usuario
            return redirect(url_for('mostrar_notas'))
        elif profesor:
            session["username"]= usuario
            return redirect(url_for('profesores.v_proestudi'))
        else:
            flash("Contraseña incorrecta")
            return redirect(url_for('index'))
    else:
        return render_template('index.html')

@app.route('/user/notas', methods=['GET'])
def mostrar_notas():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('index'))
    
    usuario = session['username']
    cedula = request.form.get('cedula')
    resultados = db.resultado.find({"cedula": usuario})
    tareas = db['tareas'].find({"cedula": usuario})

    # Agrupar notas por materia (como ya lo tienes)
    materias = defaultdict(lambda: {
        "profesor": "",
        "notas": {
            "1 Trimestre": "",
            "2 Trimestre": "",
            "3 Trimestre": "",
            "4 Trimestre": ""
        }
    })
    
    for doc in resultados:
        materia_nombre = doc["materias"]
        materias[materia_nombre]["profesor"] = doc["profesor"]
        materias[materia_nombre]["notas"][doc["bimestre"]] = doc["nota"]
    
    # Agrupar tareas por materia y deber de deber
    tareas_agrupadas = defaultdict(lambda: {
        "profesor": "",
        "notas": {
            "1 Trimestre": "",
            "2 Trimestre": "",
            "3 Trimestre": "",
            "4 Trimestre": ""
        }
    })
    
    for doc in tareas:
        clave = f"{doc['materias']} - {doc['deber']}"  # Agrupa por materia y deber de deber
        tareas_agrupadas[clave]["profesor"] = doc["profesor"]
        tareas_agrupadas[clave]["notas"][doc["bimestre"]] = doc["nota"]
    
    # Convertir el defaultdict a un diccionario normal para pasarlo a la plantilla
    datos = {
        "cedula": cedula,
        "nombre": doc["nombre"],
        "apellido": doc["apellido"],
        "paralelo": doc["paralelo"],
        "n_año": doc["n_año"],
        "materias": materias
    }
    
    # Procesar tareas agrupadas
    datos2 = {
        "cedula": cedula,
        "nombre": doc["nombre"],
        "apellido": doc["apellido"],
        "paralelo": doc["paralelo"],
        "n_año": doc["n_año"],
        "materias2": tareas_agrupadas
    }

    return render_template('/user/notas.html', datos=datos, datos2=datos2)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('index'))

    usuario = session['username']
    
    # Obtener datos de ambas colecciones
    resultados = list(db.resultado.find({"cedula": usuario}))
    tareas = list(db.tareas.find({"cedula": usuario}))
    
    # Verificar si hay datos
    if not resultados:
        flash("No hay calificaciones disponibles")
        return redirect(url_for('dashboard'))
    
    # Organizar datos de exámenes por materia y bimestre
    materias_exam = {}
    for resultado in resultados:
        materia = resultado["materias"]
        bimestre = resultado["bimestre"]
        
        if materia not in materias_exam:
            materias_exam[materia] = {
                "profesor": resultado["profesor"],
                "notas": {"1 Trimestre": "", "2 Trimestre": "", "3 Trimestre": "", "4 Trimestre": ""}
            }
        
        materias_exam[materia]["notas"][bimestre] = resultado["nota"]
    
    # Organizar datos de tareas por materia, deber y bimestre
    materias_tareas = {}
    for tarea in tareas:
        materia = tarea["materias"]
        deber = tarea["deber"]
        bimestre = tarea["bimestre"]
        clave = f"{materia} - {deber}"
        
        if clave not in materias_tareas:
            materias_tareas[clave] = {
                "profesor": tarea["profesor"],
                "notas": {"1 Trimestre": "", "2 Trimestre": "", "3 Trimestre": "", "4 Trimestre": ""}
            }
        
        materias_tareas[clave]["notas"][bimestre] = tarea["nota"]
    
    # Crear PDF
    pdf_filename = f"{usuario}_notas.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    ancho, alto = letter

    # Encabezado del PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, alto - 40, "CALIFICACIONES")
    c.setFont("Helvetica", 12)
    c.drawString(30, alto - 60, "ESCUELA PRIMARIA NO. 1234")

    # Información del estudiante
    if resultados:
        c.drawString(30, alto - 90, f"Cedula: {resultados[0]['cedula']}")
        c.drawString(30, alto - 110, f"Nombre: {resultados[0]['nombre']}")
        c.drawString(30, alto - 130, f"Apellido: {resultados[0]['apellido']}")
        c.drawString(30, alto - 150, f"Paralelo: {resultados[0]['paralelo']}")
        c.drawString(30, alto - 170, f"Año lectivo: {resultados[0]['n_año']}")
    
    y_position = alto - 200
    
    # Tabla de exámenes
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y_position, "CALIFICACIONES DE EXÁMENES")
    y_position -= 30
    
    # Cabecera de la tabla de exámenes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y_position, "MATERIA")
    c.drawString(120, y_position, "PROFESOR")
    c.drawString(220, y_position, "1 TRIM")
    c.drawString(270, y_position, "2 TRIM")
    c.drawString(320, y_position, "3 TRIM")
    c.drawString(370, y_position, "4 TRIM")
    c.drawString(440, y_position, "RESULTADO")
    
    # Línea horizontal bajo el encabezado
    y_position -= 10
    c.line(30, y_position, 520, y_position)
    y_position -= 15
    
    # Datos de exámenes
    c.setFont("Helvetica", 10)
    for materia, info in materias_exam.items():
        # Calcular el resultado promediando las notas disponibles
        notas_disponibles = [float(nota) for nota in info["notas"].values() if nota != ""]
        resultado = sum(notas_disponibles) / len(notas_disponibles) if notas_disponibles else 0
        resultado_formateado = f"{resultado:.2f}"
        
        c.drawString(30, y_position, materia)
        c.drawString(120, y_position, info["profesor"])
        c.drawString(220, y_position, str(info["notas"]["1 Trimestre"]))
        c.drawString(270, y_position, str(info["notas"]["2 Trimestre"]))
        c.drawString(320, y_position, str(info["notas"]["3 Trimestre"]))
        c.drawString(370, y_position, str(info["notas"]["4 Trimestre"]))
        c.drawString(440, y_position, resultado_formateado)
        
        y_position -= 20
        
        # Si estamos llegando al final de la página, crear una nueva
        if y_position < 100:
            c.showPage()
            y_position = alto - 50
    
    # Espacio entre tablas
    y_position -= 30
    
    # Tabla de tareas
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y_position, "CALIFICACIONES DE TAREAS")
    y_position -= 30
    
    # Cabecera de la tabla de tareas
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y_position, "MATERIA")
    c.drawString(100, y_position, "deber")
    c.drawString(150, y_position, "PROFESOR")
    c.drawString(220, y_position, "1 TRIM")
    c.drawString(270, y_position, "2 TRIM")
    c.drawString(320, y_position, "3 TRIM")
    c.drawString(370, y_position, "4 TRIM")
    c.drawString(440, y_position, "RESULTADO")
    
    # Línea horizontal bajo el encabezado
    y_position -= 10
    c.line(30, y_position, 520, y_position)
    y_position -= 15
    
    # Si no hay espacio suficiente, crear una nueva página
    if y_position < 150:
        c.showPage()
        y_position = alto - 50
        
        # Encabezado de la nueva página
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, "CALIFICACIONES DE TAREAS")
        y_position -= 30
        
        # Cabecera de la tabla de tareas
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30, y_position, "MATERIA")
        c.drawString(100, y_position, "deber")
        c.drawString(150, y_position, "PROFESOR")
        c.drawString(220, y_position, "1 TRIM")
        c.drawString(270, y_position, "2 TRIM")
        c.drawString(320, y_position, "3 TRIM")
        c.drawString(370, y_position, "4 TRIM")
        c.drawString(440, y_position, "RESULTADO")
        
        # Línea horizontal bajo el encabezado
        y_position -= 10
        c.line(30, y_position, 520, y_position)
        y_position -= 15
    
    # Datos de tareas
    c.setFont("Helvetica", 10)
    if materias_tareas:
        for clave, info in materias_tareas.items():
            materia, deber = clave.split(" - ")
            
            # Calcular el resultado promediando las notas disponibles
            notas_disponibles = [float(nota) for nota in info["notas"].values() if nota != ""]
            resultado = sum(notas_disponibles) / len(notas_disponibles) if notas_disponibles else 0
            resultado_formateado = f"{resultado:.2f}"
            
            c.drawString(30, y_position, materia)
            c.drawString(100, y_position, deber)
            c.drawString(150, y_position, info["profesor"])
            c.drawString(220, y_position, str(info["notas"]["1 Trimestre"]))
            c.drawString(270, y_position, str(info["notas"]["2 Trimestre"]))
            c.drawString(320, y_position, str(info["notas"]["3 Trimestre"]))
            c.drawString(370, y_position, str(info["notas"]["4 Trimestre"]))
            c.drawString(440, y_position, resultado_formateado)
            
            y_position -= 20
            
            # Si estamos llegando al final de la página, crear una nueva
            if y_position < 100:
                c.showPage()
                y_position = alto - 50
    else:
        c.drawString(30, y_position, "No hay tareas disponibles.")
    
    # Guardar y enviar el PDF
    c.save()
    return send_file(pdf_filename, as_attachment=True)

# *Codigo de ingreso de usuarios
app.register_blueprint(año)

# * Codigo de ingreso de estudiantes
app.register_blueprint(estudiante)

# * Codigo de ingreso de materias
app.register_blueprint(materia)

# * Codigo de almacenamiento de resultados
app.register_blueprint(resultado)

# * Codigo de almacenamiento 
app.register_blueprint(almacenamiento)

# Registrar el Blueprint
app.register_blueprint(chat_bp)

# Registrar el Blueprint
app.register_blueprint(profesores)


# Registrar el Blueprint
app.register_blueprint(tareas)

# Registrar el Blueprint
app.register_blueprint(entrada)

@app.errorhandler(404)
def notFound(error=None):
    message = {
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    return render_template('404.html', message=message), 404



if __name__ == '__main__':
    app.run(debug=True, port=4000)
