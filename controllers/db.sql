create table año(
    id_año auto_increment primary key, 
    n_año varchar(50),-- por ejemplo  primero año depende el nombre que quieran ponerle 
    paralelo varchar(10),-- los paralelos que se 
    fecha_creacion date,
)-- se refiere esta tabla a los paralelos


create table materia(
    id_materia auto_increment primary key,
    n_materia varchar(100),
    fecha_creacion date
)

create table estudiante(
    id_estudiante auto_increment primary key,
    nombre varchar(100),
    apellido varchar(100),
    cedula int(10),
    paralelo varchar(10),-- esta relacionado con la tabla año
    n_año varchar(50),-- se refiere a primer año 
    clave varchar(100),-- para que pueda el estudiante tener donde ingresar
)

create table resultado(
    id_resultados auto_increment primary key,
    nombre varchar(100),
    apellido varchar(100),
    n_año int(10),-- se refiere a primer año
    fecha_registro date,
    materias varchar(50),
    nota varchar(10),--notas del estudiante
)

create table almacenamiento(
    id_resultados auto_increment primary key,
    nombre varchar(100),
    apellido varchar(100),
    n_año int(10),-- se refiere a primer año
    fecha_registro date,
    materias varchar(50),
    nota int(10),--notas del estudiante
)-- Es lo mismo ya que se necesita saber de cada uno de los años del estudiante
