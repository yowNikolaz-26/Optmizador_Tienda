"""
Yow Nicolas Guacaneme Molano
Ivan Andres Bernal Hernandez
-----------------
Sistema de Análisis Comparativo de Configuraciones
para Algoritmos Genéticos aplicados a Sudoku 9x9
-----------------
"""
import random
import copy
import time
from datetime import datetime

# Variables globales
sudoku_inicial = []
posiciones_fijas = []

def es_valido_en_posicion(sudoku, pos, num):
    """Verifica si colocar 'num' en 'pos' es válido"""
    n = 9
    fila_idx = pos // n
    col_idx = pos % n
    
    # Verificar fila
    inicio_fila = fila_idx * n
    fin_fila = (fila_idx + 1) * n
    for p in range(inicio_fila, fin_fila):
        if sudoku[p] == num:
            return False
    
    # Verificar columna
    for f in range(n):
        if sudoku[f * n + col_idx] == num:
            return False
    
    # Verificar subcuadrante 3x3
    cuad_fila = (fila_idx // 3) * 3
    cuad_col = (col_idx // 3) * 3
    for f in range(cuad_fila, cuad_fila + 3):
        for c in range(cuad_col, cuad_col + 3):
            if sudoku[f * n + c] == num:
                return False
    
    return True

def resolver_sudoku_backtracking(sudoku, posiciones_fijas):
    """Intenta resolver el sudoku usando backtracking"""
    n = 9
    sudoku_copia = sudoku[:]
    
    def backtrack(pos):
        if pos == n * n:
            return True
        
        if pos in posiciones_fijas:
            return backtrack(pos + 1)
        
        for num in range(1, n + 1):
            if es_valido_en_posicion(sudoku_copia, pos, num):
                sudoku_copia[pos] = num
                if backtrack(pos + 1):
                    return True
                sudoku_copia[pos] = 0
        
        return False
    
    return backtrack(0)

def generar_sudoku_inicial():
    """Genera un Sudoku 9x9 SOLUCIONABLE con 5 números fijos"""
    global sudoku_inicial, posiciones_fijas
    
    n = 9
    max_intentos_generacion = 50
    intento_generacion = 0
    
    print("Generando Sudoku inicial solucionable...\n")
    
    while intento_generacion < max_intentos_generacion:
        sudoku_inicial = [0] * (n * n)
        posiciones_fijas = []
        
        posiciones_colocadas = 0
        intentos = 0
        max_intentos = 1000
        
        while posiciones_colocadas < 5 and intentos < max_intentos:
            pos = random.randint(0, n * n - 1)
            
            if pos in posiciones_fijas:
                intentos += 1
                continue
            
            disponibles = []
            for num in range(1, n + 1):
                if es_valido_en_posicion(sudoku_inicial, pos, num):
                    disponibles.append(num)
            
            if disponibles:
                numero = random.choice(disponibles)
                sudoku_inicial[pos] = numero
                posiciones_fijas.append(pos)
                posiciones_colocadas += 1
            
            intentos += 1
        
        print(f"Intento {intento_generacion + 1}: Verificando...", end=" ")
        
        if resolver_sudoku_backtracking(sudoku_inicial, posiciones_fijas):
            print("✅ ¡SOLUCIONABLE!")
            break
        else:
            print("❌ Sin solución")
            intento_generacion += 1
    
    print(f"\n{'='*70}")
    print("SUDOKU INICIAL GENERADO (será usado en todas las configuraciones)")
    print(f"{'='*70}")
    print(f"Posiciones fijas: {posiciones_fijas}")
    print(f"Valores fijos: {[sudoku_inicial[p] for p in posiciones_fijas]}")
    imprimir_sudoku(sudoku_inicial)
    print()

def funcion_objetivo(individuo):
    """Calcula el fitness del individuo"""
    n = 9
    conflictos = 0
    
    matriz = []
    for i in range(n):
        fila = individuo[i*n:(i+1)*n]
        matriz.append(fila)

    # Verificar filas
    for fila in matriz:
        conflictos += (n - len(set(fila)))

    # Verificar columnas
    for col in range(n):
        columna = [matriz[fila][col] for fila in range(n)]
        conflictos += (n - len(set(columna)))

    # Verificar subcuadrantes 3x3
    for i in range(0, n, 3):
        for j in range(0, n, 3):
            subcuadrante = []
            for x in range(i, i+3):
                for y in range(j, j+3):
                    subcuadrante.append(matriz[x][y])
            conflictos += (n - len(set(subcuadrante)))

    max_fitness = n * 3  # 27
    fitness = max_fitness - conflictos
    return fitness

def crear_individuo():
    """Crea un individuo válido"""
    n = 9
    individuo = copy.deepcopy(sudoku_inicial)
    
    for fila_idx in range(n):
        inicio = fila_idx * n
        fin = (fila_idx + 1) * n
        
        fijas_en_fila = [p for p in posiciones_fijas if inicio <= p < fin]
        valores_fijos = [individuo[p] for p in fijas_en_fila]
        
        disponibles = [x for x in range(1, n+1) if x not in valores_fijos]
        random.shuffle(disponibles)
        
        idx_disponible = 0
        for pos in range(inicio, fin):
            if pos not in posiciones_fijas:
                individuo[pos] = disponibles[idx_disponible]
                idx_disponible += 1
    
    return individuo

def crear_poblacion(tamaño):
    """Crea población inicial"""
    return [crear_individuo() for _ in range(tamaño)]

def seleccion(poblacion):
    """Selección por torneo"""
    candidatos = random.sample(poblacion, min(3, len(poblacion)))
    return max(candidatos, key=funcion_objetivo)

def cruce(padre1, padre2, tasa_cruce):
    """Cruce respetando posiciones fijas"""
    if random.random() > tasa_cruce:
        return copy.deepcopy(padre1), copy.deepcopy(padre2)
    
    n = 9
    hijo1, hijo2 = [], []
    
    for fila in range(n):
        inicio = fila * n
        fin = (fila + 1) * n

        fila_padre1 = padre1[inicio:fin]
        fila_padre2 = padre2[inicio:fin]

        if random.random() < 0.5:
            hijo1.extend(fila_padre1)
            hijo2.extend(fila_padre2)
        else:
            hijo1.extend(fila_padre2)
            hijo2.extend(fila_padre1)
    
    return hijo1, hijo2

def mutacion(individuo, tasa_mutacion):
    """Mutación sin tocar posiciones fijas"""
    if random.random() > tasa_mutacion:
        return individuo
    
    n = 9
    fila = random.randint(0, n-1)
    inicio = fila * n
    fin = (fila + 1) * n
    
    posiciones_mutables = [p for p in range(inicio, fin) if p not in posiciones_fijas]
    
    if len(posiciones_mutables) >= 2:
        pos1, pos2 = random.sample(posiciones_mutables, 2)
        individuo[pos1], individuo[pos2] = individuo[pos2], individuo[pos1]
    
    return individuo

def imprimir_sudoku(individuo):
    """Imprime el sudoku con formato visual"""
    n = 9
    print("┌───────┬───────┬───────┐")
    for i in range(n):
        if i == 3 or i == 6:
            print("├───────┼───────┼───────┤")
        
        fila_datos = individuo[i*n:(i+1)*n]
        fila_formateada = []
        
        for j, num in enumerate(fila_datos):
            pos = i * n + j
            if pos in posiciones_fijas:
                fila_formateada.append(f"*{num}*")
            elif num == 0:
                fila_formateada.append(" . ")
            else:
                fila_formateada.append(f" {num} ")
        
        grupo1 = "".join(fila_formateada[0:3])
        grupo2 = "".join(fila_formateada[3:6])
        grupo3 = "".join(fila_formateada[6:9])
        
        print(f"│{grupo1}│{grupo2}│{grupo3}│")
    
    print("└───────┴───────┴───────┘")

def calcular_diversidad(poblacion):
    """Calcula diversidad genética"""
    if len(poblacion) < 2:
        return 1.0
    
    diferencias = 0
    comparaciones = 0
    muestra = min(10, len(poblacion))
    
    for i in range(muestra):
        for j in range(i + 1, muestra):
            diff = sum(1 for a, b in zip(poblacion[i], poblacion[j]) if a != b)
            diferencias += diff
            comparaciones += 1
    
    if comparaciones == 0:
        return 0.0
    
    return diferencias / (comparaciones * len(poblacion[0]))

def algoritmo_genetico_con_estadisticas(config_nombre, tamaño_poblacion, max_generaciones, 
                                        tasa_cruce, tasa_mutacion, tasa_elitista, silencioso=False):
    """
    Ejecuta el algoritmo genético y retorna estadísticas completas
    """
    poblacion = crear_poblacion(tamaño_poblacion)
    
    # Estadísticas a recolectar
    estadisticas = {
        'config_nombre': config_nombre,
        'tamaño_poblacion': tamaño_poblacion,
        'max_generaciones': max_generaciones,
        'tasa_cruce': tasa_cruce,
        'tasa_mutacion': tasa_mutacion,
        'tasa_elitista': tasa_elitista,
        'fitness_inicial': 0,
        'fitness_final': 0,
        'mejor_fitness': 0,
        'generaciones_ejecutadas': 0,
        'tiempo_ejecucion': 0,
        'razon_parada': '',
        'diversidad_inicial': 0,
        'diversidad_final': 0,
        'convergencia_prematura': False,
        'estancamiento': False,
        'historial_fitness': [],
        'historial_diversidad': [],
        'mejor_solucion': None
    }
    
    tiempo_inicio = time.time()
    
    mejor_fitness_global = -1
    generaciones_sin_mejora = 0
    max_sin_mejora = 300
    num_elite = int(tamaño_poblacion * tasa_elitista)
    
    # Fitness inicial
    estadisticas['fitness_inicial'] = funcion_objetivo(poblacion[0])
    estadisticas['diversidad_inicial'] = calcular_diversidad(poblacion)
    
    if not silencioso:
        print(f"\n{'='*70}")
        print(f"EJECUTANDO: {config_nombre}")
        print(f"{'='*70}")
    
    for generacion in range(max_generaciones):
        # Evaluar población
        fitness_poblacion = [(ind, funcion_objetivo(ind)) for ind in poblacion]
        fitness_poblacion.sort(key=lambda x: x[1], reverse=True)
        
        mejor_individuo, fitness_mejor = fitness_poblacion[0]
        
        # Guardar estadísticas
        estadisticas['historial_fitness'].append(fitness_mejor)
        diversidad_actual = calcular_diversidad(poblacion)
        estadisticas['historial_diversidad'].append(diversidad_actual)
        
        # Verificar mejora
        if fitness_mejor > mejor_fitness_global:
            mejor_fitness_global = fitness_mejor
            generaciones_sin_mejora = 0
            if not silencioso and generacion % 50 == 0:
                print(f'Gen {generacion + 1}: fitness={fitness_mejor}/27, div={diversidad_actual:.3f}')
        else:
            generaciones_sin_mejora += 1

        # Criterios de parada
        if fitness_mejor == 27:
            estadisticas['razon_parada'] = 'Solución perfecta encontrada'
            estadisticas['generaciones_ejecutadas'] = generacion + 1
            break
        
        if generaciones_sin_mejora >= max_sin_mejora:
            estadisticas['razon_parada'] = f'Sin mejoras por {max_sin_mejora} generaciones'
            estadisticas['generaciones_ejecutadas'] = generacion + 1
            estadisticas['estancamiento'] = True
            break
        
        if diversidad_actual < 0.01:
            estadisticas['razon_parada'] = 'Pérdida crítica de diversidad'
            estadisticas['generaciones_ejecutadas'] = generacion + 1
            estadisticas['convergencia_prematura'] = True
            break
        
        # Nueva generación
        nueva_poblacion = []
        
        # Elitismo
        for i in range(num_elite):
            nueva_poblacion.append(copy.deepcopy(fitness_poblacion[i][0]))
        
        # Reproducción
        while len(nueva_poblacion) < tamaño_poblacion:
            padre1 = seleccion(poblacion)
            padre2 = seleccion(poblacion)
            hijo1, hijo2 = cruce(padre1, padre2, tasa_cruce)
            hijo1 = mutacion(hijo1, tasa_mutacion)
            hijo2 = mutacion(hijo2, tasa_mutacion)
            nueva_poblacion.extend([hijo1, hijo2])
        
        poblacion = nueva_poblacion[:tamaño_poblacion]
    
    # Si terminó por máximo de generaciones
    if estadisticas['generaciones_ejecutadas'] == 0:
        estadisticas['generaciones_ejecutadas'] = max_generaciones
        estadisticas['razon_parada'] = 'Máximo de generaciones alcanzado'
    
    # Estadísticas finales
    estadisticas['tiempo_ejecucion'] = time.time() - tiempo_inicio
    estadisticas['fitness_final'] = fitness_mejor
    estadisticas['mejor_fitness'] = mejor_fitness_global
    estadisticas['diversidad_final'] = diversidad_actual
    estadisticas['mejor_solucion'] = mejor_individuo
    
    # Detectar convergencia prematura
    if estadisticas['diversidad_final'] < 0.1 and estadisticas['fitness_final'] < 20:
        estadisticas['convergencia_prematura'] = True
    
    if not silencioso:
        print(f"Completado en {estadisticas['tiempo_ejecucion']:.2f}s")
        print(f"Fitness final: {fitness_mejor}/27")
        print(f"Razón de parada: {estadisticas['razon_parada']}")
    
    return estadisticas

def generar_reporte_comparativo(resultados):
    """Genera un reporte completo comparando todas las configuraciones"""
    print("\n" + "="*80)
    print(" "*20 + "REPORTE COMPARATIVO DE CONFIGURACIONES")
    print("="*80)
    
    # Tabla resumen
    print("\n📊 TABLA RESUMEN DE RESULTADOS:")
    print("-"*80)
    print(f"{'Config':<20} {'Fitness':<12} {'Gens':<8} {'Tiempo':<10} {'Diversidad':<12}")
    print(f"{'     ':<20} {'Final':<12} {'Ejec.':<8} {'(seg)':<10} {'Final':<12}")
    print("-"*80)
    
    for r in resultados:
        print(f"{r['config_nombre']:<20} {r['fitness_final']:>4}/27 ({r['fitness_final']/27*100:>5.1f}%) "
              f"{r['generaciones_ejecutadas']:>6} {r['tiempo_ejecucion']:>8.2f}s  "
              f"{r['diversidad_final']:>10.3f}")
    
    print("-"*80)
    
    # Mejor configuración
    mejor = max(resultados, key=lambda x: x['fitness_final'])
    print(f"\n🏆 MEJOR CONFIGURACIÓN: {mejor['config_nombre']}")
    print(f"   Fitness alcanzado: {mejor['fitness_final']}/27 ({mejor['fitness_final']/27*100:.1f}%)")
    print(f"   Generaciones usadas: {mejor['generaciones_ejecutadas']}")
    
    # Más rápida
    mas_rapida = min(resultados, key=lambda x: x['tiempo_ejecucion'])
    print(f"\n⚡ MÁS RÁPIDA: {mas_rapida['config_nombre']}")
    print(f"   Tiempo: {mas_rapida['tiempo_ejecucion']:.2f}s")
    
    # Análisis de exploración vs explotación
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE EXPLORACIÓN VS EXPLOTACIÓN")
    print("="*80)
    
    for r in resultados:
        print(f"\n{r['config_nombre']}:")
        print(f"  Parámetros: Elite={r['tasa_elitista']*100:.0f}%, Mutación={r['tasa_mutacion']*100:.0f}%, Cruce={r['tasa_cruce']*100:.0f}%")
        
        # Clasificar estrategia
        if r['tasa_mutacion'] > 0.2 and r['tasa_elitista'] < 0.1:
            estrategia = "ALTA EXPLORACIÓN"
        elif r['tasa_mutacion'] < 0.1 and r['tasa_elitista'] > 0.2:
            estrategia = "ALTA EXPLOTACIÓN"
        else:
            estrategia = "EQUILIBRADA"
        
        print(f"  Estrategia: {estrategia}")
        print(f"  Resultado: Fitness {r['fitness_final']}/27")
        print(f"  Diversidad: {r['diversidad_inicial']:.3f} → {r['diversidad_final']:.3f} "
              f"(pérdida {(1-r['diversidad_final']/r['diversidad_inicial'])*100:.1f}%)")
        
        # Diagnóstico
        if r['convergencia_prematura']:
            print(f"  ⚠️ CONVERGENCIA PREMATURA detectada")
        if r['estancamiento']:
            print(f"  ⚠️ ESTANCAMIENTO detectado")
        if r['fitness_final'] == 27:
            print(f"  ✅ SOLUCIÓN PERFECTA")
    
    # Comparación de evolución
    print("\n" + "="*80)
    print("📈 EVOLUCIÓN DEL FITNESS POR CONFIGURACIÓN")
    print("="*80)
    
    for r in resultados:
        if len(r['historial_fitness']) > 0:
            mejora_inicial = r['historial_fitness'][min(10, len(r['historial_fitness'])-1)] - r['historial_fitness'][0]
            mejora_final = r['historial_fitness'][-1] - r['historial_fitness'][max(0, len(r['historial_fitness'])-10)]
            
            print(f"\n{r['config_nombre']}:")
            print(f"  Inicial: {r['fitness_inicial']}/27")
            print(f"  Final: {r['fitness_final']}/27")
            print(f"  Mejora primeras 10 gen: {mejora_inicial:.2f}")
            print(f"  Mejora últimas 10 gen: {mejora_final:.2f}")
    
    # Conclusiones
    print("\n" + "="*80)
    print("💡 CONCLUSIONES Y RECOMENDACIONES")
    print("="*80)
    
    # Analizar qué funcionó mejor
    alta_exploracion = [r for r in resultados if r['tasa_mutacion'] > 0.2 and r['tasa_elitista'] < 0.1]
    alta_explotacion = [r for r in resultados if r['tasa_mutacion'] < 0.1 and r['tasa_elitista'] > 0.2]
    
    if alta_exploracion:
        prom_exp = sum(r['fitness_final'] for r in alta_exploracion) / len(alta_exploracion)
        print(f"\n📊 Configuraciones con ALTA EXPLORACIÓN:")
        print(f"   Fitness promedio: {prom_exp:.2f}/27")
    
    if alta_explotacion:
        prom_expl = sum(r['fitness_final'] for r in alta_explotacion) / len(alta_explotacion)
        print(f"\n📊 Configuraciones con ALTA EXPLOTACIÓN:")
        print(f"   Fitness promedio: {prom_expl:.2f}/27")
    
    print(f"\n🎯 Para este problema de Sudoku 9x9:")
    if mejor['tasa_mutacion'] > 0.15:
        print(f"   ✅ La exploración (mutación alta) fue más efectiva")
    else:
        print(f"   ✅ La explotación (elitismo alto) fue más efectiva")
    
    print(f"\n📝 Configuración óptima encontrada:")
    print(f"   - Elitismo: {mejor['tasa_elitista']*100:.0f}%")
    print(f"   - Mutación: {mejor['tasa_mutacion']*100:.0f}%")
    print(f"   - Cruce: {mejor['tasa_cruce']*100:.0f}%")
    print(f"   - Población: {mejor['tamaño_poblacion']}")
    
    print("\n" + "="*80)
    
    # Mostrar mejor solución
    print(f"\nMEJOR SOLUCIÓN ENCONTRADA ({mejor['config_nombre']}):")
    imprimir_sudoku(mejor['mejor_solucion'])
    
    return resultados

def ejecutar_experimento_comparativo():
    """
    Ejecuta 5 configuraciones diferentes sobre el MISMO sudoku inicial
    """
    print("="*80)
    print(" "*15 + "SISTEMA DE ANÁLISIS COMPARATIVO")
    print(" "*20 + "Sudoku 9x9 con Algoritmos Genéticos")
    print("="*80)
    
    # Generar UN SOLO sudoku inicial
    generar_sudoku_inicial()
    
    # Definir 5 configuraciones diferentes
    configuraciones = [
        {
            'nombre': 'Config 1: Alta Explotación',
            'poblacion': 100,
            'generaciones': 2000,
            'cruce': 0.7,
            'mutacion': 0.08,
            'elitismo': 0.30
        },
        {
            'nombre': 'Config 2: Alta Exploración',
            'poblacion': 100,
            'generaciones': 2000,
            'cruce': 0.85,
            'mutacion': 0.30,
            'elitismo': 0.05
        },
        {
            'nombre': 'Config 3: Equilibrada',
            'poblacion': 100,
            'generaciones': 2000,
            'cruce': 0.80,
            'mutacion': 0.15,
            'elitismo': 0.10
        },
        {
            'nombre': 'Config 4: Conservadora',
            'poblacion': 150,
            'generaciones': 2000,
            'cruce': 0.60,
            'mutacion': 0.05,
            'elitismo': 0.25
        },
        {
            'nombre': 'Config 5: Agresiva',
            'poblacion': 80,
            'generaciones': 2000,
            'cruce': 0.90,
            'mutacion': 0.35,
            'elitismo': 0.02
        }
    ]
    
    print(f"\n{'='*80}")
    print("Se ejecutarán las siguientes configuraciones:")
    print(f"{'='*80}")
    for i, config in enumerate(configuraciones, 1):
        print(f"{i}. {config['nombre']}")
        print(f"   Población={config['poblacion']}, Elite={config['elitismo']*100:.0f}%, "
              f"Mutación={config['mutacion']*100:.0f}%, Cruce={config['cruce']*100:.0f}%")
    
    input("\nPresiona ENTER para comenzar el experimento...")
    
    # Ejecutar cada configuración
    resultados = []
    
    for i, config in enumerate(configuraciones, 1):
        print(f"\n{'='*80}")
        print(f"EJECUTANDO CONFIGURACIÓN {i}/{len(configuraciones)}")
        print(f"{'='*80}")
        
        estadisticas = algoritmo_genetico_con_estadisticas(
            config['nombre'],
            config['poblacion'],
            config['generaciones'],
            config['cruce'],
            config['mutacion'],
            config['elitismo'],
            silencioso=False
        )
        
        resultados.append(estadisticas)
        
        print(f"✓ Configuración {i} completada")
        time.sleep(1)  # Pausa breve
    
    # Generar reporte comparativo
    print("\n\n")
    generar_reporte_comparativo(resultados)
    
    # Guardar resultados en archivo
    guardar_resultados_txt(resultados)
    
    print(f"\n{'='*80}")
    print("EXPERIMENTO COMPLETADO")
    print(f"Los resultados han sido guardados en 'resultados_sudoku.txt'")
    print(f"{'='*80}\n")

def guardar_resultados_txt(resultados):
    """Guarda los resultados en un archivo de texto para el informe"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"resultados_sudoku_{timestamp}.txt"
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(" "*20 + "REPORTE DE RESULTADOS\n")
        f.write(" "*15 + "Algoritmos Genéticos - Sudoku 9x9\n")
        f.write("="*80 + "\n\n")
        
        f.write("SUDOKU INICIAL:\n")
        f.write(f"Posiciones fijas: {posiciones_fijas}\n")
        f.write(f"Valores: {[sudoku_inicial[p] for p in posiciones_fijas]}\n\n")
        
        f.write("RESULTADOS POR CONFIGURACIÓN:\n")
        f.write("-"*80 + "\n")
        
        for r in resultados:
            f.write(f"\n{r['config_nombre']}\n")
            f.write(f"  Parámetros:\n")
            f.write(f"    - Población: {r['tamaño_poblacion']}\n")
            f.write(f"    - Elitismo: {r['tasa_elitista']*100:.1f}%\n")
            f.write(f"    - Mutación: {r['tasa_mutacion']*100:.1f}%\n")
            f.write(f"    - Cruce: {r['tasa_cruce']*100:.1f}%\n")
            f.write(f"  Resultados:\n")
            f.write(f"    - Fitness final: {r['fitness_final']}/27 ({r['fitness_final']/27*100:.1f}%)\n")
            f.write(f"    - Generaciones ejecutadas: {r['generaciones_ejecutadas']}\n")
            f.write(f"    - Tiempo: {r['tiempo_ejecucion']:.2f} segundos\n")
            f.write(f"    - Diversidad final: {r['diversidad_final']:.3f}\n")
            f.write(f"    - Razón de parada: {r['razon_parada']}\n")
            if r['convergencia_prematura']:
                f.write(f"    - ⚠️ Convergencia prematura detectada\n")
            if r['estancamiento']:
                f.write(f"    - ⚠️ Estancamiento detectado\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
    
    print(f"\n✅ Resultados guardados en: {nombre_archivo}")

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    ejecutar_experimento_comparativo()