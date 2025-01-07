class Año:
    def __init__(self,id_año,n_año,a_numero,paralelo,fecha_creacion):
        
        self.id_año=id_año
        self.n_año=n_año
        self.a_numero=a_numero
        self.paralelo=paralelo
        self.fecha_creacion=fecha_creacion
        
        
    def AñoDBCollection(self):
        return{
            'id_año':self.id_año,
            'n_año':self.n_año,
            'a_numero':self.a_numero,
            'paralelo':self.paralelo,
            'fecha_creacion':self.fecha_creacion
        }