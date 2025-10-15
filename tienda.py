"""
Optimizador de Tienda con Algoritmos Genéticos
---------------------------------------------
Este script implementa una aplicación de escritorio con Tkinter que utiliza un
algoritmo genético para determinar la distribución óptima de productos en una
tienda con un área limitada, con el objetivo de maximizar la ganancia total.

Autor: Yow Nicolas Guacaneme Molano
Fecha: 15 de Octubre de 2025
"""

# ================= LIBRERÍAS =================
import random
import copy
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


# ================= CONSTANTES Y DATOS DEL PROBLEMA =================
AREA_TOTAL_TIENDA = 50 * 10000  # 50m² convertidos a 500,000 cm²

PRODUCTOS = {
    'nevera': {
        'alto': 142.2, 'ancho': 50, 'area': 142.2 * 50,
        'valor': 1100000, 'color': '#3498db'  # Azul
    },
    'televisor': {
        'alto': 52, 'ancho': 93, 'area': 52 * 93,
        'valor': 850000, 'color': '#e74c3c'  # Rojo
    },
    'ventilador': {
        'alto': 16, 'ancho': 50, 'area': 16 * 50,
        'valor': 225000, 'color': '#2ecc71'  # Verde
    }
}

# Parámetros por defecto para el algoritmo genético
DEFAULT_TAMANO_POBLACION = 100
DEFAULT_MAX_GENERACIONES = 300
DEFAULT_TASA_CRUCE = 0.8
DEFAULT_TASA_MUTACION = 0.2
DEFAULT_TASA_ELITISMO = 0.1


# ================= FUNCIONES DEL ALGORITMO GENÉTICO =================

def crear_individuo():
    """Crea un individuo (solución) aleatorio para la población inicial.

    Un individuo es una lista de 3 enteros [neveras, televisores, ventiladores].
    Se asegura de que haya al menos uno de cada uno y llena el espacio
    hasta un porcentaje aleatorio del área total.

    Returns:
        list: Una lista representando la cantidad de cada producto.
    """
    # Se inicia con al menos un producto de cada tipo
    n_neveras, n_televisores, n_ventiladores = 1, 1, 1
    
    area_usada = (n_neveras * PRODUCTOS['nevera']['area'] +
                  n_televisores * PRODUCTOS['televisor']['area'] +
                  n_ventiladores * PRODUCTOS['ventilador']['area'])

    # Llena el espacio restante con productos aleatorios hasta un límite
    area_objetivo = AREA_TOTAL_TIENDA * random.uniform(0.7, 0.95)
    tipos_producto = list(PRODUCTOS.keys())
    
    while area_usada < area_objetivo:
        tipo = random.choice(tipos_producto)
        area_producto = PRODUCTOS[tipo]['area']
        
        if area_usada + area_producto <= AREA_TOTAL_TIENDA:
            if tipo == 'nevera': n_neveras += 1
            elif tipo == 'televisor': n_televisores += 1
            else: n_ventiladores += 1
            area_usada += area_producto
        else:
            # Si no cabe el producto elegido, se detiene para no exceder el área
            break
            
    return [n_neveras, n_televisores, n_ventiladores]

def calcular_area_total(individuo):
    """Calcula el área total ocupada por un individuo."""
    return sum(individuo[i] * list(PRODUCTOS.values())[i]['area'] for i in range(3))

def calcular_valor_total(individuo):
    """Calcula el valor total (ganancia) de un individuo."""
    return sum(individuo[i] * list(PRODUCTOS.values())[i]['valor'] for i in range(3))

def es_valido(individuo):
    """Verifica si un individuo cumple con las restricciones del problema."""
    # Restricción 1: Mínimo un producto de cada tipo
    if any(cantidad < 1 for cantidad in individuo):
        return False
    # Restricción 2: No exceder el área total
    return calcular_area_total(individuo) <= AREA_TOTAL_TIENDA

def funcion_objetivo(individuo):
    """Función de aptitud (fitness). Devuelve el valor total si es válido, 0 si no."""
    if not es_valido(individuo):
        return 0  # Penalización para soluciones inválidas
    return calcular_valor_total(individuo)

def crear_poblacion(tamano):
    """Crea una población inicial de individuos válidos."""
    return [crear_individuo() for _ in range(tamano)]

def seleccion(poblacion, funcion_objetivo):
    """Selecciona un padre usando selección por torneo."""
    # Se eligen 3 candidatos al azar y el mejor de ellos gana el torneo
    candidatos = random.sample(poblacion, k=3)
    return max(candidatos, key=funcion_objetivo)

def cruce(padre1, padre2, tasa_cruce):
    """Realiza un cruce uniforme entre dos padres si se cumple la tasa de cruce."""
    if random.random() > tasa_cruce:
        return copy.deepcopy(padre1), copy.deepcopy(padre2)
    
    hijo1, hijo2 = [], []
    for i in range(3):
        if random.random() < 0.5:
            hijo1.append(padre1[i])
            hijo2.append(padre2[i])
        else:
            hijo1.append(padre2[i])
            hijo2.append(padre1[i])
            
    return hijo1, hijo2

def mutacion(individuo, tasa_mutacion):
    """Aplica una mutación a un individuo si se cumple la tasa de mutación."""
    if random.random() > tasa_mutacion:
        return individuo
    
    # Intenta mutar hasta 5 veces para encontrar una mutación válida
    for _ in range(5):
        individuo_mutado = individuo[:]
        gen_a_mutar = random.randint(0, 2)
        
        # Decide si sumar o restar unidades del producto
        if random.random() < 0.5:
            individuo_mutado[gen_a_mutar] += random.randint(1, 3)
        else:
            individuo_mutado[gen_a_mutar] = max(1, individuo_mutado[gen_a_mutar] - random.randint(1, 2))
        
        # La mutación solo se acepta si el resultado es una solución válida
        if es_valido(individuo_mutado):
            return individuo_mutado
            
    return individuo # Si no se encuentra una mutación válida, se devuelve el original

def ejecutar_algoritmo_genetico(tamano_poblacion, max_generaciones, tasa_cruce, tasa_mutacion, tasa_elitismo, callback_progreso=None):
    """Ejecuta el ciclo principal del algoritmo genético.

    Args:
        tamano_poblacion (int): Número de individuos por generación.
        max_generaciones (int): Número máximo de iteraciones.
        tasa_cruce (float): Probabilidad de que dos padres se crucen.
        tasa_mutacion (float): Probabilidad de que un individuo mute.
        tasa_elitismo (float): Porcentaje de la población que pasa directamente a la siguiente generación.
        callback_progreso (function, optional): Función para reportar el progreso a la GUI.

    Returns:
        tuple: (mejor_individuo_global, mejor_valor_global, historial_fitness)
    """
    poblacion = crear_poblacion(tamano_poblacion)
    mejor_individuo_global = None
    mejor_valor_global = 0
    historial_fitness = []
    
    num_elite = int(tamano_poblacion * tasa_elitismo)

    for generacion in range(max_generaciones):
        # Evaluar la aptitud de toda la población
        fitness_poblacion = sorted(
            [(ind, funcion_objetivo(ind)) for ind in poblacion],
            key=lambda x: x[1], reverse=True
        )
        
        # Guardar el mejor de la generación actual
        mejor_individuo, mejor_valor = fitness_poblacion[0]
        historial_fitness.append(mejor_valor)
        
        # Actualizar el mejor global si se encuentra uno nuevo
        if mejor_valor > mejor_valor_global:
            mejor_valor_global = mejor_valor
            mejor_individuo_global = copy.deepcopy(mejor_individuo)
            if callback_progreso:
                callback_progreso(generacion, mejor_valor_global, mejor_individuo_global)
        
        # Crear la siguiente generación
        nueva_poblacion = []
        
        # 1. Elitismo: Los mejores individuos pasan directamente
        if num_elite > 0:
            elite = [copy.deepcopy(ind[0]) for ind in fitness_poblacion[:num_elite]]
            nueva_poblacion.extend(elite)
            
        # 2. Selección, Cruce y Mutación para el resto
        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = seleccion(poblacion, funcion_objetivo)
            padre2 = seleccion(poblacion, funcion_objetivo)
            hijo1, hijo2 = cruce(padre1, padre2, tasa_cruce)
            
            nueva_poblacion.append(mutacion(hijo1, tasa_mutacion))
            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(mutacion(hijo2, tasa_mutacion))
        
        poblacion = nueva_poblacion

    return mejor_individuo_global, mejor_valor_global, historial_fitness


# ================= CLASE DE LA INTERFAZ GRÁFICA (GUI) =================

class TiendaVisualizadorApp:
    """
    Clase principal para la interfaz gráfica de la aplicación.
    Gestiona todos los widgets de Tkinter y la interacción con el usuario.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Tienda - Algoritmos Genéticos")
        self.root.geometry("1400x900")
        self.root.configure(bg='#ecf0f1')
        
        self.mejor_solucion = None
        self.mejor_valor = 0
        self.historial_fitness = []
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Construye todos los elementos visuales de la aplicación."""
        # --- Creación de paneles principales (Izquierdo para controles, Derecho para gráficos) ---
        frame_izquierdo = tk.Frame(self.root, bg='#ecf0f1', width=400)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        frame_derecho = tk.Frame(self.root, bg='#ecf0f1')
        frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Panel Izquierdo: Controles y Resultados ---
        tk.Label(frame_izquierdo, text="🏪 OPTIMIZADOR DE TIENDA", 
                 font=('Arial', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        # Sección de parámetros del algoritmo
        self._crear_panel_parametros(frame_izquierdo)
        
        # Botones de acción
        self.btn_ejecutar = tk.Button(frame_izquierdo, text="▶ EJECUTAR ALGORITMO", command=self.ejecutar_optimizacion, font=('Arial', 12, 'bold'), bg='#27ae60', fg='white', cursor='hand2', height=2)
        self.btn_ejecutar.pack(pady=10, fill=tk.X, padx=20)
        
        # Barra de progreso
        self.label_progreso = tk.Label(frame_izquierdo, text="Esperando ejecución...", bg='#ecf0f1', font=('Arial', 10, 'italic'))
        self.label_progreso.pack(pady=5)
        self.progress = ttk.Progressbar(frame_izquierdo, mode='determinate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        
        # Sección de resultados
        self._crear_panel_resultados(frame_izquierdo)
        
        # --- Panel Derecho: Gráficos de Matplotlib ---
        self.fig, (self.ax_distribucion, self.ax_convergencia) = plt.subplots(
            2, 1, figsize=(9, 8), gridspec_kw={'height_ratios': [3, 2]}, constrained_layout=True
        )
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=frame_derecho)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.mostrar_mensaje_inicial()

    def _crear_panel_parametros(self, parent):
        """Crea el frame con las entradas para los parámetros del AG."""
        params_frame = tk.LabelFrame(parent, text="⚙️ Parámetros del Algoritmo", font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        params_frame.pack(fill=tk.BOTH, padx=5, pady=10)
        
        self.param_vars = {}
        parametros = {
            "Tamaño Población:": (DEFAULT_TAMANO_POBLACION, "Población de individuos en cada generación."),
            "Max Generaciones:": (DEFAULT_MAX_GENERACIONES, "Número de ciclos que el algoritmo evolucionará."),
            "Tasa Cruce (0-1):": (DEFAULT_TASA_CRUCE, "Probabilidad de que dos padres se crucen (e.g., 0.8 = 80%)."),
            "Tasa Mutación (0-1):": (DEFAULT_TASA_MUTACION, "Probabilidad de que un gen mute (e.g., 0.2 = 20%)."),
        }
        
        for label, (default_val, _) in parametros.items():
            row_frame = tk.Frame(params_frame, bg='#ecf0f1')
            row_frame.pack(fill=tk.X, padx=10, pady=4)
            tk.Label(row_frame, text=label, bg='#ecf0f1', font=('Arial', 10)).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=str(default_val))
            self.param_vars[label.split(':')[0]] = var
            entry = tk.Entry(row_frame, textvariable=var, width=10, font=('Arial', 10), justify='center')
            entry.pack(side=tk.RIGHT)

    def _crear_panel_resultados(self, parent):
        """Crea el frame para mostrar la mejor solución encontrada."""
        resultado_frame = tk.LabelFrame(parent, text="🏆 Mejor Solución", font=('Arial', 12, 'bold'), bg='#ecf0f1', fg='#34495e')
        resultado_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        self.label_resultados = tk.Label(resultado_frame, text="Los resultados aparecerán aquí.", bg='#ecf0f1', font=('Arial', 10), justify=tk.LEFT, wraplength=350)
        self.label_resultados.pack(padx=10, pady=10, anchor='w')

    def mostrar_mensaje_inicial(self):
        """Limpia y muestra los mensajes iniciales en los gráficos."""
        for ax in [self.ax_distribucion, self.ax_convergencia]:
            ax.clear()
            ax.axis('off')

        self.ax_distribucion.text(0.5, 0.5, '🏪\nPresiona "EJECUTAR ALGORITMO"', 
                                 ha='center', va='center', fontsize=18, color='#7f8c8d', transform=self.ax_distribucion.transAxes)
        self.ax_convergencia.text(0.5, 0.5, 'Gráfico de convergencia',
                                   ha='center', va='center', fontsize=12, color='#7f8c8d', transform=self.ax_convergencia.transAxes)
        self.canvas_plot.draw()
        
    def ejecutar_optimizacion(self):
        """Función principal que se llama al presionar el botón de ejecutar."""
        try:
            # Recolecta y valida los parámetros de la GUI
            tamano_pob = int(self.param_vars["Tamaño Población"].get())
            max_gen = int(self.param_vars["Max Generaciones"].get())
            tasa_cruce = float(self.param_vars["Tasa Cruce (0-1)"].get())
            tasa_mut = float(self.param_vars["Tasa Mutación (0-1)"].get())

            if not (0 <= tasa_cruce <= 1 and 0 <= tasa_mut <= 1):
                raise ValueError("Las tasas deben estar entre 0 y 1.")
        except ValueError as e:
            messagebox.showerror("Parámetro Inválido", f"Por favor, revisa los parámetros.\nError: {e}")
            return

        # Actualiza la GUI para mostrar que el proceso ha comenzado
        self.btn_ejecutar.config(state='disabled', text="OPTIMIZANDO...")
        self.progress.config(value=0, maximum=max_gen)
        self.label_progreso.config(text="Iniciando...")
        self.root.update()
        
        def actualizar_progreso(gen, valor, _):
            """Función callback para actualizar la barra de progreso desde el AG."""
            self.progress['value'] = gen + 1
            self.label_progreso.config(text=f"Generación {gen+1}: ${valor:,.0f}")
            self.root.update_idletasks()
            
        # Llama al algoritmo genético
        self.mejor_solucion, self.mejor_valor, self.historial_fitness = ejecutar_algoritmo_genetico(
            tamano_pob, max_gen, tasa_cruce, tasa_mut, DEFAULT_TASA_ELITISMO, actualizar_progreso
        )

        # Proceso finalizado, actualiza la GUI
        self.btn_ejecutar.config(state='normal', text="▶ EJECUTAR ALGORITMO")
        self.label_progreso.config(text="¡Optimización completada!")
        
        if self.mejor_solucion:
            self.mostrar_resultados()
            self.visualizar_distribucion()
            self.visualizar_convergencia()
        else:
            messagebox.showerror("Error", "No se pudo encontrar una solución válida.")

    def mostrar_resultados(self):
        """Actualiza el panel de resultados con la mejor solución."""
        if not self.mejor_solucion: return
        
        n_nev, n_tv, n_vent = self.mejor_solucion
        area_usada = calcular_area_total(self.mejor_solucion)
        
        texto = (f"💰 **GANANCIA TOTAL: ${self.mejor_valor:,.0f}**\n\n"
                 f"**Distribución:**\n"
                 f"  • Neveras: {n_nev} unidades\n"
                 f"  • Televisores: {n_tv} unidades\n"
                 f"  • Ventiladores: {n_vent} unidades\n\n"
                 f"**Uso de Espacio:**\n"
                 f"  • Área Ocupada: {area_usada/10000:.2f} / 50.00 m²\n"
                 f"  • Ocupación: {(area_usada/AREA_TOTAL_TIENDA)*100:.1f}%")
                 
        self.label_resultados.config(text=texto)

    def visualizar_distribucion(self):
        """Dibuja la distribución de productos en el gráfico superior."""
        if not self.mejor_solucion: return
        ax = self.ax_distribucion 
        ax.clear()
        
        ancho_tienda, alto_tienda = 700, 714 # Dimensiones proporcionales a 50m^2
        productos_a_dibujar = []
        for i, tipo in enumerate(PRODUCTOS.keys()):
            for _ in range(self.mejor_solucion[i]):
                productos_a_dibujar.append(PRODUCTOS[tipo])

        # Algoritmo simple de empaquetado visual (bin packing)
        x, y, max_h_fila = 5, 5, 0
        for p in sorted(productos_a_dibujar, key=lambda item: item['alto'], reverse=True):
            if x + p['ancho'] > ancho_tienda - 5:
                x = 5
                y += max_h_fila
                max_h_fila = 0
            
            rect = Rectangle((x, y), p['ancho'], p['alto'], facecolor=p['color'], edgecolor='white')
            ax.add_patch(rect)
            x += p['ancho']
            max_h_fila = max(max_h_fila, p['alto'])
            
        ax.set_xlim(0, ancho_tienda)
        ax.set_ylim(0, alto_tienda)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f'Distribución Visual de la Tienda (Valor: ${self.mejor_valor:,.0f})', fontweight='bold')
        ax.set_xlabel('Ancho (cm)')
        ax.set_ylabel('Alto (cm)')
        ax.grid(True, linestyle='--', alpha=0.5)
        self.canvas_plot.draw()

    def visualizar_convergencia(self):
        """Dibuja el gráfico de convergencia en el sub-plot inferior."""
        ax = self.ax_convergencia
        ax.clear()
        
        ax.plot(self.historial_fitness, color='#2980b9', linewidth=2)
        ax.set_title('Evolución de la Ganancia por Generación', fontsize=12)
        ax.set_xlabel('Generación')
        ax.set_ylabel('Ganancia Máxima ($)')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda val, _: f'${val/1_000_000:.1f}M')
        )
        self.canvas_plot.draw()

# ================= PUNTO DE ENTRADA DE LA APLICACIÓN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = TiendaVisualizadorApp(root)
    root.mainloop()