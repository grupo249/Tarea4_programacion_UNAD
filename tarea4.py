# ── Importaciones estándar ────────────────────────────────────────────────────
import tkinter as tk                        # Librería principal de interfaz gráfica
from tkinter import ttk, messagebox         # Widgets avanzados y cuadros de diálogo
import re                                   # Expresiones regulares para validaciones
import datetime                             # Manejo de fechas y horas
import os                                   # Operaciones con el sistema de archivos
from abc import ABC, abstractmethod         # Clases y métodos abstractos
from typing import Optional, List           # Tipos para anotaciones (documentación)


# ══════════════════════════════════════════════════════════════════════════════
# Sección 1 – Excepciones personalizadas
# Cada excepción representa un tipo de error específico del negocio.
# Heredan Exception para integrarse con el sistema de manejo de errores.
# ══════════════════════════════════════════════════════════════════════════════

class SoftwareFJError(Exception):
    #Excepción base del sistema Software FJ.
    #Todas las excepciones del negocio heredan de aquí para poder
    #capturarlas con un solo 'except SoftwareFJError'.
    
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        # Guardamos el mensaje y un código identificador del error
        super().__init__(mensaje)           # Inicializa la clase padre con el mensaje
        self.codigo = codigo                # Código corto para identificar el tipo de error
        self.timestamp = datetime.datetime.now()  # Marca de tiempo del momento del error

    def __str__(self):
        # Representación legible del error incluyendo código y hora
        return f"[{self.codigo}] {super().__str__()} ({self.timestamp.strftime('%H:%M:%S')})"


class ClienteInvalidoError(SoftwareFJError):
    #Se lanza cuando los datos de un cliente no pasan las validaciones.
    def __init__(self, campo: str, valor: str):
        # Construimos el mensaje indicando qué campo y qué valor fallaron
        super().__init__(
            f"Dato inválido en campo '{campo}': '{valor}'",
            "ERR_CLIENTE"
        )
        self.campo = campo    # Campo específico que falló (ej: "email")
        self.valor = valor    # Valor que se intentó asignar


class ServicioNoDisponibleError(SoftwareFJError):
    #Se lanza cuando se intenta usar un servicio que no está disponible.
    def __init__(self, nombre_servicio: str, razon: str = ""):
        super().__init__(
            f"Servicio '{nombre_servicio}' no disponible. {razon}",
            "ERR_SERVICIO"
        )


class ReservaInvalidaError(SoftwareFJError):
    #Se lanza cuando los parámetros de una reserva son incorrectos.
    def __init__(self, detalle: str):
        super().__init__(f"Reserva inválida: {detalle}", "ERR_RESERVA")


class DuracionInvalidaError(SoftwareFJError):
    #Se lanza cuando la duración solicitada está fuera del rango permitido.
    def __init__(self, duracion: float, minimo: float, maximo: float):
        super().__init__(
            f"Duración {duracion}h fuera del rango permitido [{minimo}h – {maximo}h]",
            "ERR_DURACION"
        )
        self.duracion = duracion
        self.minimo = minimo
        self.maximo = maximo


class CalculoCostoError(SoftwareFJError):
    #Se lanza cuando ocurre un problema durante el cálculo del costo.
    def __init__(self, motivo: str):
        super().__init__(f"Error en cálculo de costo: {motivo}", "ERR_COSTO")


class OperacionNoPermitidaError(SoftwareFJError):
    #Se lanza cuando se intenta una operación no permitida (ej: cancelar una reserva ya cancelada).
    def __init__(self, operacion: str, estado_actual: str):
        super().__init__(
            f"Operación '{operacion}' no permitida en estado '{estado_actual}'",
            "ERR_OPERACION"
        )

# Jefferson Mosquera
# Sección 2 – Clase abstracta Servicio y servicios especializados
# Implementa polimorfismo mediante métodos sobrescritos en cada subclase.

class Servicio(ABC):
    # Clase abstracta: no se puede instanciar directamente, solo sirve como plantilla
    # ABC = Abstract Base Class, importado al inicio del archivo
    """
    Clase abstracta base para todos los servicios de Software FJ.
    Define la interfaz común que deben implementar los servicios concretos.
    """
    
    # Variable de clase compartida por todas las instancias
    # Cuenta cuántos servicios se han creado en total
    _contador_servicios: int = 0

    def __init__(self, nombre: str, precio_base: float, disponible: bool = True):
        # Constructor: se ejecuta cada vez que se crea un objeto de una subclase
        # nombre: str → el nombre del servicio debe ser texto
        # precio_base: float → el precio por hora debe ser número decimal
        # disponible: bool = True → por defecto el servicio está disponible

        # Validación 1: el nombre no puede estar vacío ni ser solo espacios
        if not nombre or not nombre.strip():
            raise ServicioNoDisponibleError("desconocido", "El nombre del servicio no puede estar vacío.")
        
        # Validación 2: el precio no puede ser negativo
        if precio_base < 0:
            raise CalculoCostoError(f"El precio base no puede ser negativo: {precio_base}")

        # Aumentamos el contador cada vez que se crea un servicio
        Servicio._contador_servicios += 1
        
        # Atributo privado (doble guión bajo __): no se puede acceder desde fuera de la clase
        # Se genera un ID único como SRV-0001, SRV-0002, etc.
        self.__id_servicio: str = f"SRV-{Servicio._contador_servicios:04d}"
        
        # .strip() elimina espacios al inicio y al final del nombre
        self.__nombre: str = nombre.strip()
        
        # Guardamos el precio base como atributo privado
        self.__precio_base: float = precio_base
        
        # Guardamos si el servicio está disponible o no
        self.__disponible: bool = disponible

    # Propiedades (getters y setters encapsulados)
    # @property permite acceder al atributo privado como si fuera público
    # pero sin poder modificarlo directamente (encapsulación)

    @property
    def id_servicio(self) -> str:
        # Getter: permite leer el ID pero no modificarlo (no tiene setter)
        return self.__id_servicio

    @property
    def nombre(self) -> str:
        # Getter: permite leer el nombre pero no modificarlo
        return self.__nombre

    @property
    def precio_base(self) -> float:
        # Getter: permite leer el precio base
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, nuevo_precio: float):
        # Setter: permite modificar el precio base con validación
        # Si el nuevo precio es negativo, lanza excepción
        if nuevo_precio < 0:
            raise CalculoCostoError(f"El precio base no puede ser negativo: {nuevo_precio}")
        # Si pasa la validación, actualiza el precio
        self.__precio_base = nuevo_precio

    @property
    def disponible(self) -> bool:
        # Getter: permite leer si el servicio está disponible
        return self.__disponible

    @disponible.setter
    def disponible(self, estado: bool):
        # Setter: permite cambiar la disponibilidad del servicio
        self.__disponible = estado

    # Métodos abstractos que cada subclase DEBE implementar
    # @abstractmethod obliga a las subclases a implementar estos métodos
    # Si una subclase no los implementa, Python lanza un error al instanciarla

    @abstractmethod
    def calcular_costo(self, duracion: float) -> float:
        """Calcula el costo base del servicio según la duración en horas."""
        pass  # pass indica que este método no tiene código aquí, la subclase lo define

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion: float) -> bool:
        """Valida que los parámetros del servicio sean correctos."""
        pass

    # Métodos concretos compartidos por todas las subclases
    # Estos métodos SÍ tienen código y son heredados por todas las subclases

    def calcular_costo_con_impuesto(self, duracion: float, impuesto: float = 0.19) -> float:
        # Método sobrecargado: variante de calcular_costo que agrega impuesto
        # impuesto = 0.19 por defecto (IVA colombiano del 19%)
        """
        Variante sobrecargada: calcula el costo incluyendo impuesto.
        Por defecto aplica IVA colombiano del 19%.
        """
        try:
            # Primero calcula el costo base llamando al método de la subclase
            costo_base = self.calcular_costo(duracion)
            
            # Valida que el impuesto esté entre 0% y 100%
            if impuesto < 0 or impuesto > 1:
                raise CalculoCostoError(f"El impuesto debe estar entre 0 y 1, se recibió: {impuesto}")
            
            # Multiplica el costo por (1 + impuesto): ej. 1.19 para IVA del 19%
            # round(..., 2) redondea a 2 decimales
            return round(costo_base * (1 + impuesto), 2)
        
        except SoftwareFJError:
            # Si el error ya es nuestro, lo relanza sin modificar
            raise
        except Exception as e:
            # Cualquier otro error inesperado lo envuelve en nuestro error personalizado
            # "from e" encadena la excepción original para no perder el detalle del error
            raise CalculoCostoError(f"Error inesperado al aplicar impuesto: {e}") from e

    def calcular_costo_con_descuento(self, duracion: float, descuento: float = 0.0) -> float:
        # Método sobrecargado: variante que aplica un descuento porcentual
        # descuento = 0.0 por defecto (sin descuento)
        """
        Variante sobrecargada: calcula el costo aplicando un descuento porcentual.
        descuento debe ser un valor entre 0 y 1 (ej: 0.10 = 10%).
        """
        try:
            # Calcula el costo base
            costo_base = self.calcular_costo(duracion)
            
            # Valida que el descuento esté entre 0% y 100%
            if descuento < 0 or descuento > 1:
                raise CalculoCostoError(f"El descuento debe estar entre 0 y 1, se recibió: {descuento}")
            
            # Multiplica por (1 - descuento): ej. 0.90 para descuento del 10%
            return round(costo_base * (1 - descuento), 2)
        
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error inesperado al aplicar descuento: {e}") from e

    def calcular_costo_completo(self, duracion: float, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        # Método sobrecargado: aplica descuento primero y luego impuesto
        # Es el costo final real que pagaría el cliente
        """
        Variante sobrecargada: aplica primero el descuento y luego el impuesto.
        Representa el costo final que paga el cliente.
        """
        try:
            # Paso 1: aplica el descuento sobre el costo base
            costo_con_descuento = self.calcular_costo_con_descuento(duracion, descuento)
            
            # Validación del impuesto
            if impuesto < 0 or impuesto > 1:
                raise CalculoCostoError(f"Impuesto inválido: {impuesto}")
            
            # Paso 2: aplica el impuesto sobre el costo ya descontado
            return round(costo_con_descuento * (1 + impuesto), 2)
        
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error en cálculo completo: {e}") from e

    def verificar_disponibilidad(self) -> None:
        # Método que lanza excepción si el servicio no está disponible
        # Lo llaman calcular_costo de cada subclase antes de calcular
        """Lanza excepción si el servicio no está disponible."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre, "El servicio está marcado como no disponible.")

    def __str__(self) -> str:
        # Método especial: define cómo se muestra el objeto con print()
        estado = "Disponible" if self.__disponible else "No disponible"
        return f"[{self.__id_servicio}] {self.__nombre} | Precio base: ${self.__precio_base:,.2f}/h | {estado}"



# Servicio 1 – Reserva de Sala

class ReservaSala(Servicio):
    # Hereda de Servicio: obtiene todos sus atributos y métodos automáticamente
    """
    Servicio de reserva de salas de reunión o conferencia.
    El costo depende del precio base por hora y la capacidad de la sala.
    """

    # Constantes de clase: definen el rango válido de duración para este servicio
    DURACION_MINIMA: float = 1.0    # Mínimo 1 hora
    DURACION_MAXIMA: float = 12.0   # Máximo 12 horas seguidas

    def __init__(self, nombre: str, precio_base: float, capacidad: int, disponible: bool = True):
        # Llama al constructor de la clase padre (Servicio) con sus parámetros
        super().__init__(nombre, precio_base, disponible)
        
        # Validación específica de ReservaSala: la capacidad debe ser positiva
        if capacidad <= 0:
            raise ClienteInvalidoError("capacidad", str(capacidad))
        
        # Atributo privado específico de esta clase
        self.__capacidad: int = capacidad  # Número máximo de personas

    @property
    def capacidad(self) -> int:
        # Getter para leer la capacidad de la sala
        return self.__capacidad

    def validar_parametros(self, duracion: float) -> bool:
        # Implementación obligatoria del método abstracto
        # Verifica que la duración esté entre 1 y 12 horas
        """Valida que la duración esté dentro del rango permitido para salas."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            # Si está fuera del rango, lanza excepción con los límites
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True  # Si pasa la validación, retorna True

    def calcular_costo(self, duracion: float) -> float:
        # Implementación obligatoria del método abstracto
        # Fórmula: precio_base * horas (+ 15% si capacidad > 20)
        """
        Costo = precio_base * duracion.
        Si la sala tiene capacidad mayor a 20 personas, se aplica recargo del 15%.
        """
        try:
            # Paso 1: verifica que el servicio esté disponible
            self.verificar_disponibilidad()
            
            # Paso 2: valida que la duración sea correcta
            self.validar_parametros(duracion)
            
            # Paso 3: calcula el costo base
            costo = self.precio_base * duracion
            
            # Paso 4: si la sala es grande (más de 20 personas), aplica recargo
            if self.__capacidad > 20:
                costo *= 1.15  # Multiplica por 1.15 = agrega 15% al costo
            
            # round(..., 2) redondea a 2 decimales para evitar errores de punto flotante
            return round(costo, 2)
        
        except SoftwareFJError:
            # Si el error ya es nuestro, lo relanza sin modificar
            raise
        except Exception as e:
            # Cualquier otro error inesperado lo envuelve en nuestro error
            raise CalculoCostoError(f"Error calculando costo de sala: {e}") from e

    def describir(self) -> str:
        # Implementación obligatoria del método abstracto
        # Retorna un texto con los detalles del servicio usando f-strings
        return (
            f"Reserva de Sala '{self.nombre}' | "
            f"Capacidad: {self.__capacidad} personas | "
            f"Precio: ${self.precio_base:,.2f}/h | "      # :,.2f = formato con comas y 2 decimales
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )

# Servicio 2 – Alquiler de Equipo

class AlquilerEquipo(Servicio):
    # Hereda de Servicio igual que ReservaSala
    """
    Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, etc.).
    Incluye un depósito de garantía obligatorio.
    """

    DURACION_MINIMA: float = 0.5    # Mínimo 30 minutos (0.5 horas)
    DURACION_MAXIMA: float = 72.0   # Máximo 3 días (72 horas)

    def __init__(self, nombre: str, precio_base: float, tipo_equipo: str,
                 deposito_garantia: float, disponible: bool = True):
        # Llama al constructor padre
        super().__init__(nombre, precio_base, disponible)
        
        # Validación: el tipo de equipo no puede estar vacío
        if not tipo_equipo or not tipo_equipo.strip():
            raise ServicioNoDisponibleError(nombre, "El tipo de equipo no puede estar vacío.")
        
        # Validación: el depósito no puede ser negativo
        if deposito_garantia < 0:
            raise CalculoCostoError(f"El depósito de garantía no puede ser negativo: {deposito_garantia}")
        
        # Atributos privados específicos de AlquilerEquipo
        self.__tipo_equipo: str = tipo_equipo.strip()          # Ej: "Portátil", "Proyector"
        self.__deposito_garantia: float = deposito_garantia    # Monto fijo que se cobra una sola vez

    @property
    def tipo_equipo(self) -> str:
        # Getter para el tipo de equipo
        return self.__tipo_equipo

    @property
    def deposito_garantia(self) -> float:
        # Getter para el depósito de garantía
        return self.__deposito_garantia

    def validar_parametros(self, duracion: float) -> bool:
        # Verifica que la duración esté entre 0.5 y 72 horas
        """Valida que la duración esté dentro del rango permitido para equipos."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True

    def calcular_costo(self, duracion: float) -> float:
        # Fórmula: (precio_base * horas) + depósito_garantía
        # El depósito se cobra UNA SOLA VEZ sin importar cuántas horas sean
        """
        Costo = precio_base * duracion + depósito de garantía.
        El depósito se cobra una sola vez independiente de la duración.
        """
        try:
            self.verificar_disponibilidad()   # Verifica disponibilidad
            self.validar_parametros(duracion) # Valida rango de duración
            
            # Suma el costo por horas más el depósito fijo
            costo = (self.precio_base * duracion) + self.__deposito_garantia
            return round(costo, 2)
        
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error calculando costo de equipo: {e}") from e

    def describir(self) -> str:
        # Descripción detallada del servicio de alquiler
        return (
            f"Alquiler de Equipo '{self.nombre}' | "
            f"Tipo: {self.__tipo_equipo} | "
            f"Precio: ${self.precio_base:,.2f}/h + "
            f"Depósito: ${self.__deposito_garantia:,.2f} | "
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )

# Servicio 3 – Asesoría Especializada

class AsesoriaEspecializada(Servicio):
    # Hereda de Servicio
    """
    Servicio de asesoría técnica o profesional especializada.
    El costo varía según el nivel del asesor (junior, senior, experto).
    """

    DURACION_MINIMA: float = 1.0    # Mínimo 1 hora
    DURACION_MAXIMA: float = 8.0    # Máximo 1 jornada laboral (8 horas)

    # Diccionario de clase: mapea cada nivel con su multiplicador de precio
    # junior  → precio normal  (x1.0)
    # senior  → precio x1.5   (50% más caro)
    # experto → precio x2.0   (el doble)
    NIVELES_VALIDOS = {
        "junior":  1.0,
        "senior":  1.5,
        "experto": 2.0
    }

    def __init__(self, nombre: str, precio_base: float, especialidad: str,
                 nivel_asesor: str, disponible: bool = True):
        # Llama al constructor padre
        super().__init__(nombre, precio_base, disponible)
        
        # Validación: la especialidad no puede estar vacía
        if not especialidad or not especialidad.strip():
            raise ServicioNoDisponibleError(nombre, "La especialidad no puede estar vacía.")
        
        # Convierte el nivel a minúsculas para comparación sin importar mayúsculas
        nivel = nivel_asesor.strip().lower()
        
        # Validación: el nivel debe ser uno de los permitidos
        if nivel not in self.NIVELES_VALIDOS:
            raise ServicioNoDisponibleError(
                nombre,
                f"Nivel '{nivel_asesor}' inválido. Use: {list(self.NIVELES_VALIDOS.keys())}"
            )
        
        # Atributos privados específicos de AsesoriaEspecializada
        self.__especialidad: str = especialidad.strip()  # Ej: "Programación", "Redes"
        self.__nivel_asesor: str = nivel                 # Guardamos en minúsculas

    @property
    def especialidad(self) -> str:
        # Getter para la especialidad
        return self.__especialidad

    @property
    def nivel_asesor(self) -> str:
        # Getter para el nivel del asesor
        return self.__nivel_asesor

    def validar_parametros(self, duracion: float) -> bool:
        # Verifica que la duración esté entre 1 y 8 horas
        """Valida que la duración esté dentro del rango permitido para asesorías."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True

    def calcular_costo(self, duracion: float) -> float:
        # Fórmula: precio_base * horas * multiplicador_según_nivel
        """
        Costo = precio_base * duracion * multiplicador_nivel.
        Un asesor experto cuesta el doble que uno junior.
        """
        try:
            self.verificar_disponibilidad()   # Verifica disponibilidad
            self.validar_parametros(duracion) # Valida rango de duración
            
            # Obtiene el multiplicador del diccionario según el nivel
            multiplicador = self.NIVELES_VALIDOS[self.__nivel_asesor]
            
            # Calcula el costo aplicando el multiplicador
            costo = self.precio_base * duracion * multiplicador
            return round(costo, 2)
        
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error calculando costo de asesoría: {e}") from e

    def describir(self) -> str:
        # Obtiene el multiplicador para mostrarlo en la descripción
        multiplicador = self.NIVELES_VALIDOS[self.__nivel_asesor]
        return (
            f"Asesoría '{self.nombre}' | "
            f"Especialidad: {self.__especialidad} | "
            # .capitalize() pone la primera letra en mayúscula: "senior" → "Senior"
            f"Nivel: {self.__nivel_asesor.capitalize()} (x{multiplicador}) | "
            f"Precio: ${self.precio_base:,.2f}/h | "
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )

# Bloque de prueba principal

if __name__ == "__main__":
    print("=== Probando Servicios ===\n")

    # Prueba ReservaSala
    try:
        sala = ReservaSala("Sala Azul", 50000, 10)
        print(sala.describir())
        print(f"Costo 2h: ${sala.calcular_costo(2):,.2f}")
        print(f"Costo con IVA: ${sala.calcular_costo_con_impuesto(2):,.2f}")
    except SoftwareFJError as e:
        print(f"Error: {e}")

    print()

    # Prueba AlquilerEquipo
    try:
        equipo = AlquilerEquipo("Portátil HP", 20000, "Portátil", 50000)
        print(equipo.describir())
        print(f"Costo 3h: ${equipo.calcular_costo(3):,.2f}")
    except SoftwareFJError as e:
        print(f"Error: {e}")

    print()

    # Prueba AsesoriaEspecializada
    try:
        asesoria = AsesoriaEspecializada("Asesoría Python", 80000, "Programación", "senior")
        print(asesoria.describir())
        print(f"Costo 2h: ${asesoria.calcular_costo(2):,.2f}")
        print(f"Costo con descuento 10%: ${asesoria.calcular_costo_con_descuento(2, 0.10):,.2f}")
    except SoftwareFJError as e:
        print(f"Error: {e}")

    print()

    # Prueba con error intencional
    try:
        sala_mala = ReservaSala("Sala Roja", 50000, -5)
    except SoftwareFJError as e:
        print(f"Error esperado capturado: {e}")