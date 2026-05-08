# Tarea4_programacion_UNAD
Tarea 4 de programación - Componente práctico - Prácticas simuladas

# Software FJ – Sistema de Gestión de Reservas

Aplicación de escritorio desarrollada en Python con interfaz gráfica Tkinter para gestionar clientes, servicios y reservas de una empresa.

---

## Descripción

Software FJ permite registrar clientes, crear servicios (salas, equipos, asesorías) y gestionar reservas con cálculo automático de costos, validaciones de negocio y registro de eventos en log.

---

## Requisitos

- Python 3.8 o superior
- Librerías: `tkinter` (incluida en Python estándar), `re`, `datetime`, `os`, `abc`

> No requiere instalación de dependencias externas.

---

## Cómo ejecutar

```bash
python Tarea4.py
```

---

## Estructura del proyecto

Tarea4.py             # Archivo principal con toda la lógica y la GUI
software_fj.log       # Archivo de log generado automáticamente al ejecutar
README.md             # Este archivo

---

## Funcionalidades

### Gestión de Clientes
- Registro de clientes con nombre, email y teléfono
- Validación automática de formato de email y teléfono

### Gestión de Servicios
Tres tipos disponibles:
- **Reserva de Sala** – precio por hora, recargo si capacidad > 20 personas
- **Alquiler de Equipo** – precio por hora + depósito de garantía
- **Asesoría Especializada** – precio según nivel del asesor (junior, senior, experto)

### Gestión de Reservas
- Asignación de cliente y servicio
- Validación de duración según tipo de servicio
- Cálculo automático del costo total
- Estados de reserva: pendiente → confirmada → procesada / cancelada

---

## Conceptos aplicados

| Concepto | Aplicación |
|---|---|
| Herencia | `Cliente` hereda de `EntidadBase`; servicios heredan de `Servicio` |
| Abstracción | Clases abstractas `EntidadBase` y `Servicio` con métodos abstractos |
| Polimorfismo | `calcular_costo()` se comporta diferente en cada tipo de servicio |
| Encapsulamiento | Atributos privados con getters y setters en `Cliente` y `Servicio` |
| Excepciones personalizadas | Jerarquía propia heredando de `SoftwareFJError` |

---

## Registro de eventos (Log)

La aplicación genera automáticamente el archivo `software_fj.log` con cada sesión, registrando creaciones exitosas y errores con marca de tiempo.

---

## Autores

- Luiza Fernanda Cespedes 
- Nicol vanessa Castillo Castillo
- Jackeline Alegria Sinisterra 
- Jefferson Mosquera Meneses
- Gabriel Alejandro Suarez Cifuentes

## Grupo 249
