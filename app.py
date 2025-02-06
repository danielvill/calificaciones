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
import io

db = dbase()
app = Flask(__name__)
app.secret_key = 'calificaciones'




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
        if usuario_fo:
            session["username"]= usuario
            return redirect(url_for('año.v_año'))
        elif estudiante:
            session["username"]= usuario
            return redirect(url_for('mostrar_notas'))
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
    resultados = db.resultado.find({"cedula": usuario})
    datos = []

    for resultado in resultados:
        datos.append({
            "cedula": resultado["cedula"],
            "nombre": resultado["nombre"],
            "apellido": resultado["apellido"],
            "paralelo": resultado["paralelo"],
            "n_año": resultado["n_año"],
            "fecha_creacion": resultado["fecha_creacion"],
            "materia": resultado["materias"],
            "nota": resultado["nota"],
            "bimestre": resultado["bimestre"]
        })

    return render_template('/user/notas.html', datos=datos)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('index'))

    usuario = session['username']
    resultados = db.resultado.find({"cedula": usuario})
    datos = []

    for resultado in resultados:
        datos.append({
            "cedula": resultado["cedula"],
            "nombre": resultado["nombre"],
            "apellido": resultado["apellido"],
            "paralelo": resultado["paralelo"],
            "n_año": resultado["n_año"],
            "materia": resultado["materias"],
            "nota": resultado["nota"],
            "bimestre": resultado["bimestre"]
        })
        
    pdf_filename = f"{usuario}_notas.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    ancho, alto = letter

    c.drawString(30, alto - 40, "CALIFICACIONES")
    c.drawString(30, alto - 60, "ESCUELA PRIMARIA NO. 1234")
    c.drawString(30, alto - 80, f"Cedula: {datos[0]['cedula']}")
    c.drawString(30, alto - 100, f"Nombre: {datos[0]['nombre']}")
    c.drawString(30, alto - 120, f"Apellido: {datos[0]['apellido']}")
    c.drawString(30, alto - 140, f"Paralelo: {datos[0]['paralelo']}")
    c.drawString(30, alto - 160, f"Año lectivo: {datos[0]['n_año']}")

    c.drawString(30, alto - 200, "MATERIAS")
    bimestres = ["1 Bimestre", "2 Bimestre", "3 Bimestre", "4 Bimestre"]
    x_offset = 200
    for bimestre in bimestres:
        c.drawString(x_offset, alto - 200, bimestre)
        x_offset += 100

    y_offset = alto - 220
    for dato in datos:
        c.drawString(30, y_offset, dato['materia'])
        x_offset = 200
        for bimestre in bimestres:
            if dato['bimestre'] == bimestre:
                c.drawString(x_offset, y_offset, str(dato['nota']))
            x_offset += 100
        y_offset -= 20
    
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




@app.errorhandler(404)
def notFound(error=None):
    message = {
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    return render_template('404.html', message=message), 404



if __name__ == '__main__':
    app.run(debug=True, port=4000)
