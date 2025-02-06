class Resultado:
    def __init__(self,id_resultado,cedula,nombre,apellido,paralelo,n_año,fecha_creacion,materias,bimestre,nota):
        
        self.id_resultado=id_resultado
        self.cedula=cedula
        self.nombre=nombre
        self.apellido=apellido
        self.paralelo=paralelo
        self.n_año=n_año
        self.fecha_creacion=fecha_creacion
        self.materias=materias
        self.bimestre=bimestre
        self.nota=nota
        
        
        
    def ResultadoDBCollection(self):
        return{
            'id_resultado':self.id_resultado,
            "cedula":self.cedula,
            'nombre':self.nombre,
            'apellido':self.apellido,
            "paralelo":self.paralelo,
            'n_año':self.n_año,
            'fecha_creacion':self.fecha_creacion,
            'materias':self.materias,
            'bimestre':self.bimestre,
            'nota':self.nota
            
        }