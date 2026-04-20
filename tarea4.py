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
