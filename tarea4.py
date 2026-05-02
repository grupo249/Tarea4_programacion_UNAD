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


# Sección 2 – Logger (Registro de eventos del archivo)
# Escribe cada evento o error en un archivo de texto con fecha y hora.

class Logger:

    #Gestiona la escritura de eventos y errores en un archivo de log.
    #El archivo se crea automáticamente si no existe.
    #Cada línea tiene formato:  [YYYY-MM-DD HH:MM:SS] [NIVEL] mensaje
    

    # Niveles de log disponibles
    INFO  = "INFO "    # Evento normal (se añaden espacios para alinear columnas)
    WARN  = "WARN "    # Advertencia
    ERROR = "ERROR"    # Error grave

    def __init__(self, ruta_archivo: str = "software_fj.log"):
        
    # Inicializa el logger con la ruta del archivo donde se guardarán los eventos.
    # Si la carpeta no existe se intenta crear.
        
        self.ruta = ruta_archivo            # Ruta completa o nombre del archivo de log

        try:
            # Intentamos crear/abrir el archivo en modo 'append' (agregar al final)
            with open(self.ruta, "a", encoding="utf-8") as f:
                # Escribimos una línea de separación al inicio de cada sesión
                f.write(f"\n{'='*70}\n")
                f.write(f"  SESIÓN INICIADA: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*70}\n")
        except OSError as e:
            # Si no se puede crear el archivo, mostramos advertencia en consola pero no detenemos el programa
            print(f"[LOGGER] Advertencia: no se pudo crear el archivo de log '{self.ruta}': {e}")

    def _escribir(self, nivel: str, mensaje: str):
        
        #Método interno que escribe una línea en el archivo de log.
        #También imprime en la consola para depuración.
         
        # Construimos la línea con formato estándar
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{timestamp}] [{nivel}] {mensaje}\n"

        try:
        # Abrimos el archivo en modo 'append' para no sobreescribir
            with open(self.ruta, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError:
        # Si el archivo no está disponible, solo mostramos en consola
            pass

        # Imprimimos en consola sin salto de línea extra (linea ya lo tiene)
        print(linea, end="")

    def info(self, mensaje: str):
        #Registra un evento informativo normal.
        self._escribir(self.INFO, mensaje)

    def warn(self, mensaje: str):
        # Registra una advertencia (algo puede salir mal).
        self._escribir(self.WARN, mensaje)

    def error(self, mensaje: str, excepcion: Optional[Exception] = None):
       
    #Registra un error. Si se proporciona la excepción, agrega su tipo
    #y mensaje para tener más contexto en el log.
        
        if excepcion:
            # Incluimos el tipo de excepción y su mensaje completo
            detalle = f"{mensaje} → {type(excepcion).__name__}: {excepcion}"
        else:
            detalle = mensaje
        self._escribir(self.ERROR, detalle)

# Sección 3 – Clase abstracta base

class EntidadBase(ABC):
   
    #Clase abstracta raíz del sistema.
    #Todas las entidades (Cliente, Servicio, Reserva) heredan de aquí.
    #Garantiza que cada entidad tenga un identificador único y pueda
    #describirse de forma legible.
    

    # Contador de clase compartido entre TODAS las instancias de EntidadBase
    # Se incrementa cada vez que se crea una nueva entidad
    _contador_global: int = 0

    def __init__(self):
        # Incrementamos el contador y asignamos un ID único a esta instancia
        EntidadBase._contador_global += 1
        self._id = EntidadBase._contador_global   # ID numérico único
        # Fecha y hora exacta de creación de la entidad
        self._fecha_creacion = datetime.datetime.now()

    @property
    def id(self) -> int:
     #Propiedad de solo lectura para acceder al ID.
        return self._id

    @property
    def fecha_creacion(self) -> datetime.datetime:
    #Propiedad de solo lectura para acceder a la fecha de creación.
        return self._fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        
        #Método abstracto: cada clase derivada DEBE implementarlo.
        #Debe retornar una cadena descriptiva de la entidad.
        
        pass  # 'pass' indica que el método no tiene cuerpo aquí; es la subclase quien lo define

    @abstractmethod
    def validar(self) -> bool:
        
       # Método abstracto: cada clase derivada DEBE implementarlo.
       # Debe retornar True si la entidad es válida, False en caso contrario.
        
        pass

    def __repr__(self) -> str:
        #Representación técnica de la entidad para depuración.
        return f"{self.__class__.__name__}(id={self._id})"



# Sección 4 – Clase abstracta Servicio y servicios especializados
# Implementa polimorfismo mediante métodos sobrescritos en cada subclase.


class Servicio(ABC):
    """
    Clase abstracta base para todos los servicios de Software FJ.
    Define la interfaz común que deben implementar los servicios concretos.
    """

    # Contador de servicios creados (variable de clase compartida)
    _contador_servicios: int = 0

    def __init__(self, nombre: str, precio_base: float, disponible: bool = True):
        # Validaciones básicas antes de asignar
        if not nombre or not nombre.strip():
            raise ServicioNoDisponibleError("desconocido", "El nombre del servicio no puede estar vacío.")
        if precio_base < 0:
            raise CalculoCostoError(f"El precio base no puede ser negativo: {precio_base}")

        Servicio._contador_servicios += 1
        self.__id_servicio: str = f"SRV-{Servicio._contador_servicios:04d}"  # ID único encapsulado
        self.__nombre: str = nombre.strip()
        self.__precio_base: float = precio_base
        self.__disponible: bool = disponible

    #  Propiedades (getters y setters encapsulados)

    @property
    def id_servicio(self) -> str:
        return self.__id_servicio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def precio_base(self) -> float:
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, nuevo_precio: float):
        if nuevo_precio < 0:
            raise CalculoCostoError(f"El precio base no puede ser negativo: {nuevo_precio}")
        self.__precio_base = nuevo_precio

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self.__disponible = estado

    #  Métodos abstractos que cada subclase DEBE implementar 

    @abstractmethod
    def calcular_costo(self, duracion: float) -> float:
        """Calcula el costo base del servicio según la duración en horas."""
        pass

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion: float) -> bool:
        """Valida que los parámetros del servicio sean correctos."""
        pass

    #  Métodos concretos compartidos por todas las subclases 

    def calcular_costo_con_impuesto(self, duracion: float, impuesto: float = 0.19) -> float:
        """
        Variante sobrecargada: calcula el costo incluyendo impuesto.
        Por defecto aplica IVA colombiano del 19%.
        """
        try:
            costo_base = self.calcular_costo(duracion)
            if impuesto < 0 or impuesto > 1:
                raise CalculoCostoError(f"El impuesto debe estar entre 0 y 1, se recibió: {impuesto}")
            return round(costo_base * (1 + impuesto), 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error inesperado al aplicar impuesto: {e}") from e

    def calcular_costo_con_descuento(self, duracion: float, descuento: float = 0.0) -> float:
        """
        Variante sobrecargada: calcula el costo aplicando un descuento porcentual.
        descuento debe ser un valor entre 0 y 1 (ej: 0.10 = 10%).
        """
        try:
            costo_base = self.calcular_costo(duracion)
            if descuento < 0 or descuento > 1:
                raise CalculoCostoError(f"El descuento debe estar entre 0 y 1, se recibió: {descuento}")
            return round(costo_base * (1 - descuento), 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error inesperado al aplicar descuento: {e}") from e

    def calcular_costo_completo(self, duracion: float, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """
        Variante sobrecargada: aplica primero el descuento y luego el impuesto.
        Representa el costo final que paga el cliente.
        """
        try:
            costo_con_descuento = self.calcular_costo_con_descuento(duracion, descuento)
            if impuesto < 0 or impuesto > 1:
                raise CalculoCostoError(f"Impuesto inválido: {impuesto}")
            return round(costo_con_descuento * (1 + impuesto), 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error en cálculo completo: {e}") from e

    def verificar_disponibilidad(self) -> None:
        """Lanza excepción si el servicio no está disponible."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre, "El servicio está marcado como no disponible.")

    def __str__(self) -> str:
        estado = "Disponible" if self.__disponible else "No disponible"
        return f"[{self.__id_servicio}] {self.__nombre} | Precio base: ${self.__precio_base:,.2f}/h | {estado}"



# Servicio 1 – Reserva de Sala

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o conferencia.
    El costo depende del precio base por hora y la capacidad de la sala.
    """

    DURACION_MINIMA: float = 1.0    # Mínimo 1 hora
    DURACION_MAXIMA: float = 12.0   # Máximo 12 horas seguidas

    def __init__(self, nombre: str, precio_base: float, capacidad: int, disponible: bool = True):
        super().__init__(nombre, precio_base, disponible)
        if capacidad <= 0:
            raise ClienteInvalidoError("capacidad", str(capacidad))
        self.__capacidad: int = capacidad  # Número máximo de personas

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def validar_parametros(self, duracion: float) -> bool:
        """Valida que la duración esté dentro del rango permitido para salas."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True

    def calcular_costo(self, duracion: float) -> float:
        """
        Costo = precio_base * duracion.
        Si la sala tiene capacidad mayor a 20 personas, se aplica recargo del 15%.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion)
            costo = self.precio_base * duracion
            if self.__capacidad > 20:
                costo *= 1.15  # Recargo por sala grande
            return round(costo, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error calculando costo de sala: {e}") from e

    def describir(self) -> str:
        return (
            f"Reserva de Sala '{self.nombre}' | "
            f"Capacidad: {self.__capacidad} personas | "
            f"Precio: ${self.precio_base:,.2f}/h | "
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )



# Servicio 2 – Alquiler de Equipo

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, etc.).
    Incluye un depósito de garantía obligatorio.
    """

    DURACION_MINIMA: float = 0.5    # Mínimo 30 minutos
    DURACION_MAXIMA: float = 72.0   # Máximo 3 días (72 horas)

    def __init__(self, nombre: str, precio_base: float, tipo_equipo: str,
                 deposito_garantia: float, disponible: bool = True):
        super().__init__(nombre, precio_base, disponible)
        if not tipo_equipo or not tipo_equipo.strip():
            raise ServicioNoDisponibleError(nombre, "El tipo de equipo no puede estar vacío.")
        if deposito_garantia < 0:
            raise CalculoCostoError(f"El depósito de garantía no puede ser negativo: {deposito_garantia}")
        self.__tipo_equipo: str = tipo_equipo.strip()
        self.__deposito_garantia: float = deposito_garantia

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def deposito_garantia(self) -> float:
        return self.__deposito_garantia

    def validar_parametros(self, duracion: float) -> bool:
        """Valida que la duración esté dentro del rango permitido para equipos."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True

    def calcular_costo(self, duracion: float) -> float:
        """
        Costo = precio_base * duracion + depósito de garantía.
        El depósito se cobra una sola vez independiente de la duración.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion)
            costo = (self.precio_base * duracion) + self.__deposito_garantia
            return round(costo, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error calculando costo de equipo: {e}") from e

    def describir(self) -> str:
        return (
            f"Alquiler de Equipo '{self.nombre}' | "
            f"Tipo: {self.__tipo_equipo} | "
            f"Precio: ${self.precio_base:,.2f}/h + "
            f"Depósito: ${self.__deposito_garantia:,.2f} | "
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )



# Servicio 3 – Asesoría Especializada

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica o profesional especializada.
    El costo varía según el nivel del asesor (junior, senior, experto).
    """

    DURACION_MINIMA: float = 1.0    # Mínimo 1 hora
    DURACION_MAXIMA: float = 8.0    # Máximo 1 jornada laboral

    # Multiplicadores de costo según nivel del asesor
    NIVELES_VALIDOS = {
        "junior":  1.0,
        "senior":  1.5,
        "experto": 2.0
    }

    def __init__(self, nombre: str, precio_base: float, especialidad: str,
                 nivel_asesor: str, disponible: bool = True):
        super().__init__(nombre, precio_base, disponible)
        if not especialidad or not especialidad.strip():
            raise ServicioNoDisponibleError(nombre, "La especialidad no puede estar vacía.")
        nivel = nivel_asesor.strip().lower()
        if nivel not in self.NIVELES_VALIDOS:
            raise ServicioNoDisponibleError(
                nombre,
                f"Nivel '{nivel_asesor}' inválido. Use: {list(self.NIVELES_VALIDOS.keys())}"
            )
        self.__especialidad: str = especialidad.strip()
        self.__nivel_asesor: str = nivel

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    @property
    def nivel_asesor(self) -> str:
        return self.__nivel_asesor

    def validar_parametros(self, duracion: float) -> bool:
        """Valida que la duración esté dentro del rango permitido para asesorías."""
        if not (self.DURACION_MINIMA <= duracion <= self.DURACION_MAXIMA):
            raise DuracionInvalidaError(duracion, self.DURACION_MINIMA, self.DURACION_MAXIMA)
        return True

    def calcular_costo(self, duracion: float) -> float:
        """
        Costo = precio_base * duracion * multiplicador_nivel.
        Un asesor experto cuesta el doble que uno junior.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion)
            multiplicador = self.NIVELES_VALIDOS[self.__nivel_asesor]
            costo = self.precio_base * duracion * multiplicador
            return round(costo, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoCostoError(f"Error calculando costo de asesoría: {e}") from e

    def describir(self) -> str:
        multiplicador = self.NIVELES_VALIDOS[self.__nivel_asesor]
        return (
            f"Asesoría '{self.nombre}' | "
            f"Especialidad: {self.__especialidad} | "
            f"Nivel: {self.__nivel_asesor.capitalize()} (x{multiplicador}) | "
            f"Precio: ${self.precio_base:,.2f}/h | "
            f"Rango permitido: {self.DURACION_MINIMA}h – {self.DURACION_MAXIMA}h"
        )

class Cliente(EntidadBase):
    # Contador para generar IDs únicos tipo CLI-001, CLI-002...
    _contador_id = 1

    def __init__(self, nombre: str, email: str, telefono: str):
        super().__init__()  # Inicializa la clase abstracta base EntidadBase
        # Asignamos ID único al cliente
        self._id_cliente = f"CLI-{Cliente._contador_id:03d}"
        Cliente._contador_id += 1

        # Usamos setters para validar cada dato desde el inicio
        self.nombre = nombre        # Llama al setter de nombre
        self.email = email          # Llama al setter de email
        self.telefono = telefono    # Llama al setter de teléfono

        # Lista interna donde se guardan las reservas del cliente
        self._reservas: List = []

    # --- Getter y Setter de nombre ---
    @property
    def nombre(self) -> str:
        return self._nombre         # Retorna el nombre almacenado

    @nombre.setter
    def nombre(self, valor: str):
        try:
            # El nombre no puede estar vacío ni tener menos de 2 caracteres
            if not valor or not valor.strip() or len(valor.strip()) < 2:
                raise ClienteInvalidoError("nombre", str(valor))
            self._nombre = valor.strip()    # Guardamos sin espacios extras
        except ClienteInvalidoError:
            raise   # Relanzamos para que el sistema la capture

    # --- Getter y Setter de email ---
    @property
    def email(self) -> str:
        return self._email          # Retorna el email almacenado

    @email.setter
    def email(self, valor: str):
        try:
            # Validamos formato de email con expresión regular
            patron = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
            if not valor or not re.match(patron, valor):
                raise ClienteInvalidoError("email", str(valor))
            self._email = valor.lower()     # Guardamos en minúsculas
        except ClienteInvalidoError:
            raise   # Relanzamos la excepción

    # --- Getter y Setter de teléfono ---
    @property
    def telefono(self) -> str:
        return self._telefono       # Retorna el teléfono almacenado

    @telefono.setter
    def telefono(self, valor: str):
        try:
            # El teléfono debe tener entre 7 y 15 dígitos numéricos
            if not valor or not valor.strip().isdigit() or not (7 <= len(valor.strip()) <= 15):
                raise ClienteInvalidoError("telefono", str(valor))
            self._telefono = valor.strip()  # Guardamos sin espacios
        except ClienteInvalidoError:
            raise   # Relanzamos la excepción

    # --- Getter de id_cliente (solo lectura) ---
    @property
    def id_cliente(self) -> str:
        return self._id_cliente     # Retorna el ID del cliente

    # --- Getter de reservas (solo lectura) ---
    @property
    def reservas(self) -> List:
        return list(self._reservas) # Retorna copia de la lista

    def agregar_reserva(self, reserva) -> None:
        # Agrega una reserva a la lista interna del cliente
        self._reservas.append(reserva)

    def describir(self) -> str:
        # Implementación del método abstracto de EntidadBase
        return (f"Cliente [{self._id_cliente}] - {self._nombre} | "
                f"Email: {self._email} | Tel: {self._telefono} | "
                f"Reservas activas: {len(self._reservas)}")

    def validar(self) -> bool:
        # Implementación del método abstracto de EntidadBase. Retorna True si los campos obligatorios están diligenciados correctamente. Como los setters ya hacen la validación estricta, aquí solo confirmamos que los atributos existan y tengan contenido.
        if self._nombre and self._email and self._telefono:
            return True
        return False

    def __str__(self) -> str:
        # Representación legible del cliente para mostrar en pantalla
        return self.describir()


# Sección 6 – Clase Reserva y duracion de estados
# Gestiona las reservas realizadas por los clientes, con estado y validaciones de duracion.

class ReservaError(Exception):
    """Excepción base para errores de reserva"""
    pass

class EstadoInvalidoError(ReservaError):
    """Se lanza cuando una operación no es válida para el estado actual"""
    pass

class DuracionReservaInvalidaError(ReservaError):
    """Se lanza cuando la duración no es válida"""
    pass

class Reserva:
    def __init__(self, cliente, servicio, duracion):
        if duracion <= 0:
            raise DuracionReservaInvalidaError("La duración debe ser mayor a 0.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion  # en horas
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
                f"Duración: {self.duracion} horas, Estado: {self.estado}")

class SoftwareFJ_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Panel de Pruebas")
        self.root.geometry("600x500")
        
        # Inicializar el logger y las listas de la aplicacion
        self.logger = Logger()
        self.clientes = []
        self.servicios = []
        self.reservas = []

        # Crear un sistema de pestanas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Frames para cada pestaña
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_servicios = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text='Gestión Clientes')
        self.notebook.add(self.tab_servicios, text='Gestión Servicios')
        self.notebook.add(self.tab_reservas, text='Gestión Reservas')

        self.init_clientes()
        self.init_servicios()
        self.init_reservas()


    # PESTANA: CLIENTES

    def init_clientes(self):
        frame_form = ttk.LabelFrame(self.tab_clientes, text="Nuevo Cliente")
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_cli_nombre = ttk.Entry(frame_form)
        self.entry_cli_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_cli_email = ttk.Entry(frame_form)
        self.entry_cli_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cli_telefono = ttk.Entry(frame_form)
        self.entry_cli_telefono.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame_form, text="Crear Cliente", command=self.crear_cliente).grid(row=3, column=0, columnspan=2, pady=10)

        self.list_clientes = tk.Listbox(self.tab_clientes)
        self.list_clientes.pack(fill="both", expand=True, padx=10, pady=5)

    def crear_cliente(self):
        try:
            # Se prueba instanciar, validando los datos
            nuevo_cliente = Cliente(
                self.entry_cli_nombre.get(),
                self.entry_cli_email.get(),
                self.entry_cli_telefono.get()
            )
            self.clientes.append(nuevo_cliente)
            self.actualizar_listas()
            self.logger.info(f"Cliente creado exitosamente: {nuevo_cliente.id_cliente}")
            messagebox.showinfo("Éxito", f"Cliente {nuevo_cliente.nombre} creado correctamente.")
        except SoftwareFJError as e:
            # En caso de error, se muestra un mensaje al usuario
            self.logger.error("Fallo al crear cliente", e)
            messagebox.showerror("Error de Validación", str(e))


    # PESTANA: SERVICIOS

    def init_servicios(self):
        frame_form = ttk.LabelFrame(self.tab_servicios, text="Nuevo Servicio")
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_srv_tipo = ttk.Combobox(frame_form, values=["Sala", "Equipo", "Asesoría"], state="readonly")
        self.combo_srv_tipo.current(0)
        self.combo_srv_tipo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_srv_nombre = ttk.Entry(frame_form)
        self.entry_srv_nombre.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Precio Base:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_srv_precio = ttk.Entry(frame_form)
        self.entry_srv_precio.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame_form, text="Crear Servicio (Rápido)", command=self.crear_servicio).grid(row=3, column=0, columnspan=2, pady=10)

        self.list_servicios = tk.Listbox(self.tab_servicios)
        self.list_servicios.pack(fill="both", expand=True, padx=10, pady=5)

    def crear_servicio(self):
        tipo = self.combo_srv_tipo.get()
        nombre = self.entry_srv_nombre.get()
        try:
            precio = float(self.entry_srv_precio.get())
            
            # Para mantener la interfaz simple, quemamos algunos valores según el tipo
            if tipo == "Sala":
                servicio = ReservaSala(nombre, precio, capacidad=10)
            elif tipo == "Equipo":
                servicio = AlquilerEquipo(nombre, precio, tipo_equipo="Computador", deposito_garantia=50000)
            else:
                servicio = AsesoriaEspecializada(nombre, precio, especialidad="Sistemas", nivel_asesor="junior")
                
            self.servicios.append(servicio)
            self.actualizar_listas()
            self.logger.info(f"Servicio creado: {servicio.id_servicio}")
            messagebox.showinfo("Éxito", f"Servicio {servicio.nombre} creado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "El precio base debe ser un número válido.")
        except SoftwareFJError as e:
            self.logger.error("Fallo al crear servicio", e)
            messagebox.showerror("Error de Servicio", str(e))

    
    # PESTANA: RESERVAS

    def init_reservas(self):
        frame_form = ttk.LabelFrame(self.tab_reservas, text="Nueva Reserva")
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_res_cli = ttk.Combobox(frame_form, state="readonly")
        self.combo_res_cli.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Servicio:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_res_srv = ttk.Combobox(frame_form, state="readonly")
        self.combo_res_srv.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Duración (h):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_res_duracion = ttk.Entry(frame_form)
        self.entry_res_duracion.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame_form, text="Crear Reserva", command=self.crear_reserva).grid(row=3, column=0, columnspan=2, pady=10)

        self.list_reservas = tk.Listbox(self.tab_reservas)
        self.list_reservas.pack(fill="both", expand=True, padx=10, pady=5)

    def crear_reserva(self):
        idx_cli = self.combo_res_cli.current()
        idx_srv = self.combo_res_srv.current()
        
        if idx_cli == -1 or idx_srv == -1:
            messagebox.showwarning("Atención", "Debe seleccionar un cliente y un servicio.")
            return

        cliente = self.clientes[idx_cli]
        servicio = self.servicios[idx_srv]

        try:
            duracion = float(self.entry_res_duracion.get())
            
            # Se valida la duracion en el calculo de costo y lo llamamos para forzar el error si lo hay
            servicio.validar_parametros(duracion)

            reserva = Reserva(cliente, servicio, duracion)
            cliente.agregar_reserva(reserva)
            self.reservas.append(reserva)
            
            self.actualizar_listas()
            self.logger.info(f"Reserva creada para {cliente.nombre} en servicio {servicio.nombre}")
            
            # Aplicamos el polimorfismo para calcular el total
            total = reserva.calcular_total()
            messagebox.showinfo("Éxito", f"Reserva creada. Costo calculado: ${total:,.2f}")

        except ValueError:
            messagebox.showerror("Error", "La duración debe ser un número válido.")
        except (SoftwareFJError, ReservaError) as e:
            self.logger.error("Fallo al crear reserva", e)
            messagebox.showerror("Error en Reserva", str(e))

    
    # UTILIDADES
    def actualizar_listas(self):
        # Actualizar listbox
        self.list_clientes.delete(0, tk.END)
        self.combo_res_cli['values'] = []
        nombres_cli = []
        for c in self.clientes:
            self.list_clientes.insert(tk.END, str(c))
            nombres_cli.append(c.nombre)
        self.combo_res_cli['values'] = nombres_cli

        self.list_servicios.delete(0, tk.END)
        self.combo_res_srv['values'] = []
        nombres_srv = []
        for s in self.servicios:
            self.list_servicios.insert(tk.END, str(s))
            nombres_srv.append(s.nombre)
        self.combo_res_srv['values'] = nombres_srv

        self.list_reservas.delete(0, tk.END)
        for r in self.reservas:
            self.list_reservas.insert(tk.END, str(r))

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJ_GUI(root)
    root.mainloop()

    