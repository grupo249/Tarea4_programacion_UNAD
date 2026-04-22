class ReservaError(Exception):
    """Excepción base para errores de reserva"""
    pass


class EstadoInvalidoError(ReservaError):
    """Se lanza cuando una operación no es válida para el estado actual"""
    pass


class DuracionInvalidaError(ReservaError):
    """Se lanza cuando la duración no es válida"""
    pass


class Reserva:
    def __init__(self, cliente, servicio, duracion):
        if duracion <= 0:
            raise DuracionInvalidaError("La duración debe ser mayor a 0.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion  # en minutos
        self.estado = "pendiente"

    def confirmar(self):
        if self.estado != "pendiente":
            raise EstadoInvalidoError("Solo se pueden confirmar reservas pendientes.")
        self.estado = "confirmada"

    def cancelar(self):
        if self.estado == "cancelada":
            raise EstadoInvalidoError("La reserva ya está cancelada.")
        if self.estado == "procesada":
            raise EstadoInvalidoError("No se puede cancelar una reserva ya procesada.")
        self.estado = "cancelada"

    def procesar(self):
        if self.estado != "confirmada":
            raise EstadoInvalidoError("Solo se pueden procesar reservas confirmadas.")
        self.estado = "procesada"

    def calcular_total(self):
        # Aquí aplicas polimorfismo del servicio
        return self.servicio.calcular_costo(self.duracion)

    def __str__(self):
        return (f"Cliente: {self.cliente}, Servicio: {self.servicio}, "
                f"Duración: {self.duracion} min, Estado: {self.estado}")