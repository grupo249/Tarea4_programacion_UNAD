import tkinter as tk
from tkinter import ttk, messagebox
import tarea4 

class SoftwareFJ_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Panel de Pruebas")
        self.root.geometry("600x500")
        
        # Inicializar el logger y las listas de la aplicacion
        self.logger = tarea4.Logger()
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
            nuevo_cliente = tarea4.Cliente(
                self.entry_cli_nombre.get(),
                self.entry_cli_email.get(),
                self.entry_cli_telefono.get()
            )
            self.clientes.append(nuevo_cliente)
            self.actualizar_listas()
            self.logger.info(f"Cliente creado exitosamente: {nuevo_cliente.id_cliente}")
            messagebox.showinfo("Éxito", f"Cliente {nuevo_cliente.nombre} creado correctamente.")
        except tarea4.SoftwareFJError as e:
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
                servicio = tarea4.ReservaSala(nombre, precio, capacidad=10)
            elif tipo == "Equipo":
                servicio = tarea4.AlquilerEquipo(nombre, precio, tipo_equipo="Computador", deposito_garantia=50000)
            else:
                servicio = tarea4.AsesoriaEspecializada(nombre, precio, especialidad="Sistemas", nivel_asesor="junior")
                
            self.servicios.append(servicio)
            self.actualizar_listas()
            self.logger.info(f"Servicio creado: {servicio.id_servicio}")
            messagebox.showinfo("Éxito", f"Servicio {servicio.nombre} creado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "El precio base debe ser un número válido.")
        except tarea4.SoftwareFJError as e:
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

            reserva = tarea4.Reserva(cliente, servicio, duracion)
            cliente.agregar_reserva(reserva)
            self.reservas.append(reserva)
            
            self.actualizar_listas()
            self.logger.info(f"Reserva creada para {cliente.nombre} en servicio {servicio.nombre}")
            
            # Aplicamos el polimorfismo para calcular el total
            total = reserva.calcular_total()
            messagebox.showinfo("Éxito", f"Reserva creada. Costo calculado: ${total:,.2f}")

        except ValueError:
            messagebox.showerror("Error", "La duración debe ser un número válido.")
        except (tarea4.SoftwareFJError, tarea4.ReservaError) as e:
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

    