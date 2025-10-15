# Optimizador de Tienda con Algoritmos Genéticos

Este proyecto es una aplicación de escritorio desarrollada en Python que utiliza un **algoritmo genético** para resolver un problema de optimización combinatoria: maximizar la ganancia de una tienda distribuyendo tres tipos de productos (neveras, televisores y ventiladores) en un área limitada de 50 m².

## Características Principales

- **Motor de Optimización Genético:** Implementa un algoritmo genético desde cero para evolucionar y encontrar la mejor combinación de productos.
- **Interfaz Gráfica Interactiva:** Creada con Tkinter, permite al usuario configurar los parámetros del algoritmo (tamaño de población, generaciones, tasas de cruce/mutación) y ejecutar la simulación.
- **Visualización de Resultados:** Muestra la solución óptima de forma clara, incluyendo la ganancia total, el área utilizada y la cantidad de cada producto.
- **Representación Gráfica:** Utiliza Matplotlib para generar dos gráficos:
    1.  Una **distribución visual** del empaquetado de los productos en el plano de la tienda.
    2.  Un **gráfico de convergencia** que muestra cómo mejora la solución a lo largo de las generaciones.


## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3
- **Librerías:**
    - **Tkinter:** Para la interfaz gráfica de usuario (GUI).
    - **Matplotlib:** Para la generación de gráficos y visualizaciones de datos.

## 🚀 Instalación y Uso

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

**1. Clona o descarga el repositorio:**
```bash
# Si usas git
git clone [https://github.com/yowNikolaz-26/Optmizador_Tienda.git](https://github.com/yowNikolaz-26/Optmizador_Tienda.git)
cd nombre-del-directorio
```

**2. (Recomendado) Crea un entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

**3. Instala las dependencias:**
El proyecto solo necesita `matplotlib`. Instálalo usando el archivo `requirements.txt`.
```bash
pip install -r requirements.txt
```

**4. Ejecuta la aplicación:**
```bash
python tu_archivo_principal.py
```
La interfaz gráfica se abrirá. Ajusta los parámetros si lo deseas y presiona "EJECUTAR ALGORITMO" para comenzar la optimización.