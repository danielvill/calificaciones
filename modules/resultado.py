class Resultado:
    def __init__(self,id_resultado,nombre,apellido,n_año,fecha_registro,materias,nota):
        
        self.id_resultado=id_resultado
        self.nombre=nombre
        self.apellido=apellido
        self.n_año=n_año
        self.fecha_registro=fecha_registro
        self.materias=materias
        self.nota=nota
        
        
        
    def ResultadoDBCollection(self):
        return{
            'id_resultado':self.id_resultado,
            'nombre':self.nombre,
            'apellido':self.apellido,
            'n_año':self.n_año,
            'fecha_registro':self.fecha_registro,
            'materias':self.materias,
            'nota':self.nota
            
        }