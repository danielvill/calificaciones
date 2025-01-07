class Estudiante:
    def __init__(self,id_estudiante,nombre,apellido,cedula,paralelo,n_año,clave):
        
        self.id_estudiante=id_estudiante
        self.nombre=nombre
        self.apellido=apellido
        self.cedula=cedula
        self.paralelo=paralelo
        self.n_año=n_año
        self.clave=clave
        
        
    def EstudianteDBCollection(self):
        return{
            'id_estudiante':self.id_estudiante,
            'nombre':self.nombre,
            'apellido':self.apellido,
            'cedula':self.cedula,
            'paralelo':self.paralelo,
            'n_año':self.n_año,
            'clave':self.clave
        }