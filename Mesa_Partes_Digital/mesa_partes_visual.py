"""Mesa de Partes Digital con interfaz gráfica (Tkinter).

Ejecutar desde VS Code: python mesa_partes_visual.py
Los expedientes se guardan en expedientes.csv junto a este archivo.
"""

import csv
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


RUTA = Path(__file__).resolve().parent / "expedientes.csv"
CAMPOS = ["codigo", "fecha", "solicitante", "dni", "tipo", "asunto", "area"]


def cargar():
    if not RUTA.exists():
        return []
    with RUTA.open("r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != CAMPOS:
            raise ValueError("El archivo expedientes.csv tiene columnas diferentes.")
        return list(lector)


def guardar(registros):
    # Guardar primero en un temporal para no perder el archivo anterior si falla.
    temporal = RUTA.with_suffix(".tmp")
    with temporal.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(registros)
    temporal.replace(RUTA)


class MesaPartes(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mesa de Partes Digital | Fundamentos de Programación")
        self.geometry("1050x690")
        self.minsize(850, 600)
        self.configure(bg="#eef3f9")
        try:
            self.registros = cargar()
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror("Error al abrir datos", str(exc) + "\nNo se sobrescribirá el archivo.")
            self.destroy()
            return

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TNotebook.Tab", padding=(15, 9), font=("Segoe UI", 10))

        cabecera = tk.Frame(self, bg="#16365f", padx=25, pady=20)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text="MESA DE PARTES DIGITAL", bg="#16365f", fg="white",
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(cabecera, text="Registro, consulta y ordenamiento de expedientes",
                 bg="#16365f", fg="#d7e9ff", font=("Segoe UI", 11)).pack(anchor="w")

        principal = ttk.Frame(self, padding=22)
        principal.pack(fill="both", expand=True)
        barra = ttk.Frame(principal)
        barra.pack(fill="x", pady=(0, 14))
        self.estado = tk.StringVar(value="Listo. Los datos se guardan en expedientes.csv")
        ttk.Button(barra, text="1. Registrar", command=lambda: self.pestanas.select(0)).pack(side="left", padx=(0, 8))
        ttk.Button(barra, text="2. Buscar", command=lambda: self.pestanas.select(1)).pack(side="left", padx=8)
        ttk.Button(barra, text="3. Ordenar y listar", command=self.ver_listado).pack(side="left", padx=8)
        ttk.Button(barra, text="4. Salir", command=self.destroy).pack(side="right")

        self.pestanas = ttk.Notebook(principal)
        self.pestanas.pack(fill="both", expand=True)
        registro = ttk.Frame(self.pestanas, padding=22)
        busqueda = ttk.Frame(self.pestanas, padding=22)
        listado = ttk.Frame(self.pestanas, padding=16)
        self.pestanas.add(registro, text="Registrar expediente")
        self.pestanas.add(busqueda, text="Buscar por código")
        self.pestanas.add(listado, text="Expedientes ordenados")
        self.campos = {}
        etiquetas = [("solicitante", "Nombre del solicitante"), ("dni", "DNI (8 dígitos)"),
                     ("tipo", "Tipo de documento"), ("asunto", "Asunto"),
                     ("area", "Área de destino")]
        for indice, (nombre, etiqueta) in enumerate(etiquetas):
            ttk.Label(registro, text=etiqueta + ":").grid(row=indice, column=0, sticky="w", pady=11)
            entrada = ttk.Entry(registro, width=55, font=("Segoe UI", 11))
            entrada.grid(row=indice, column=1, sticky="ew", padx=15, pady=11)
            self.campos[nombre] = entrada
        registro.columnconfigure(1, weight=1)
        ttk.Button(registro, text="Guardar expediente", command=self.registrar).grid(
            row=len(etiquetas), column=1, sticky="e", padx=15, pady=15)

        ttk.Label(busqueda, text="Escribe el código del expediente (ej.: MP-00001 o 1):").pack(anchor="w")
        linea = ttk.Frame(busqueda)
        linea.pack(fill="x", pady=12)
        self.codigo_busqueda = ttk.Entry(linea, width=25, font=("Segoe UI", 12))
        self.codigo_busqueda.pack(side="left", padx=(0, 12))
        ttk.Button(linea, text="Buscar expediente", command=self.buscar).pack(side="left")
        self.detalle = tk.Text(busqueda, height=13, wrap="word", font=("Consolas", 11),
                              bg="white", relief="solid", bd=1)
        self.detalle.pack(fill="both", expand=True, pady=10)
        self.detalle.configure(state="disabled")

        columnas = ("codigo", "fecha", "solicitante", "dni", "tipo", "area")
        contenedor = ttk.Frame(listado)
        contenedor.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings")
        titulos = {"codigo": "Código", "fecha": "Fecha", "solicitante": "Solicitante",
                   "dni": "DNI", "tipo": "Documento", "area": "Área"}
        for columna in columnas:
            self.tabla.heading(columna, text=titulos[columna])
            self.tabla.column(columna, width=135 if columna != "solicitante" else 190, anchor="w")
        yscroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        xscroll = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        ttk.Label(principal, textvariable=self.estado, padding=(0, 12)).pack(anchor="w")
        self.actualizar_tabla()

    def registrar(self):
        datos = {nombre: entrada.get().strip() for nombre, entrada in self.campos.items()}
        if any(not dato for dato in datos.values()):
            messagebox.showwarning("Faltan datos", "Completa todos los campos del formulario.")
            return
        dni = datos["dni"]
        if len(dni) != 8 or not dni.isascii() or not dni.isdigit():
            messagebox.showwarning("DNI incorrecto", "El DNI debe tener exactamente 8 números.")
            return
        nuevo_numero = max((int(r["codigo"].split("-")[-1]) for r in self.registros), default=0) + 1
        expediente = {"codigo": f"MP-{nuevo_numero:05d}",
                      "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **datos}
        try:
            guardar(self.registros + [expediente])
        except OSError as exc:
            messagebox.showerror("Error al guardar", str(exc))
            return
        self.registros.append(expediente)
        for entrada in self.campos.values():
            entrada.delete(0, tk.END)
        self.actualizar_tabla()
        self.estado.set(f"Expediente {expediente['codigo']} guardado correctamente.")
        messagebox.showinfo("Registro exitoso", f"Expediente guardado.\nCódigo: {expediente['codigo']}")

    def buscar(self):
        texto = self.codigo_busqueda.get().strip().upper().removeprefix("MP-")
        if not texto.isascii() or not texto.isdigit() or int(texto) == 0:
            messagebox.showwarning("Código inválido", "Ingresa un código válido, por ejemplo MP-00001.")
            return
        codigo = f"MP-{int(texto):05d}"
        resultado = next((r for r in self.registros if r["codigo"] == codigo), None)
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", tk.END)
        if resultado:
            nombres = {"codigo": "Código", "fecha": "Fecha", "solicitante": "Solicitante",
                       "dni": "DNI", "tipo": "Documento", "asunto": "Asunto", "area": "Área"}
            self.detalle.insert(tk.END, "EXPEDIENTE ENCONTRADO\n\n")
            for campo in CAMPOS:
                self.detalle.insert(tk.END, f"{nombres[campo]}: {resultado[campo]}\n")
        else:
            self.detalle.insert(tk.END, "No se encontró un expediente con ese código.")
        self.detalle.configure(state="disabled")

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for registro in sorted(self.registros, key=lambda r: int(r["codigo"].split("-")[-1])):
            self.tabla.insert("", "end", values=tuple(registro[c] for c in
                                                      ("codigo", "fecha", "solicitante", "dni", "tipo", "area")))

    def ver_listado(self):
        self.actualizar_tabla()
        self.pestanas.select(2)
        self.estado.set(f"Expedientes guardados: {len(self.registros)}")


if __name__ == "__main__":
    MesaPartes().mainloop()
