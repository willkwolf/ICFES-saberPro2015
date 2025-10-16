# Metodología ICFES - SABER PRO

## 📋 Sobre el Examen SABER PRO

### Propósito institucional

El examen SABER PRO (antes ECAES) es una evaluación estandarizada aplicada por el **ICFES** (Instituto Colombiano para la Evaluación de la Educación) a estudiantes que están próximos a culminar programas de pregrado en Colombia.

**Objetivos:**
1. Evaluar competencias genéricas y específicas desarrolladas durante la formación universitaria
2. Servir como referencia para la comparación entre programas e instituciones
3. Proporcionar información para el mejoramiento de la calidad educativa
4. Ser criterio complementario (no único) para decisiones de selección laboral

---

## 🎯 Estructura del Examen (2015)

### Sesión 1: Competencias Genéricas (Obligatorias)

Todos los estudiantes, independientemente de su programa, presentan:

| Módulo | Descripción | N° Preguntas | Tiempo |
|--------|-------------|--------------|--------|
| **Comunicación Escrita** | Producción textual argumentativa | 1 texto (350-400 palabras) | 60 min |
| **Razonamiento Cuantitativo** | Interpretación y representación matemática | 30-35 | 60 min |
| **Lectura Crítica** | Comprensión y análisis textual | 35-40 | 60 min |
| **Competencias Ciudadanas** | Conocimientos y habilidades ciudadanas | 30-35 | 60 min |
| **Inglés** | Comprensión lectora en inglés | 40-45 | 60 min |

### Sesión 2: Competencias Específicas

Para **Ingeniería** (mi caso):

| Módulo | Descripción | N° Preguntas | Tiempo |
|--------|-------------|--------------|--------|
| **Formulación de Proyectos** | Identificación, formulación y evaluación | 30-35 | 90 min |
| **Pensamiento Científico** | Matemáticas y Estadística aplicadas | 30-35 | 90 min |
| **Diseño de Sistemas** | Productivos y Logísticos (Industrial) | 30-35 | 90 min |

---

## 📊 Proceso de Calificación

### 1. Puntuación bruta
- Cada pregunta correcta suma 1 punto
- No hay penalización por respuestas incorrectas
- Puntaje bruto = Total de respuestas correctas

### 2. Estandarización (Teoría de Respuesta al Ítem - TRI)

El ICFES utiliza **IRT (Item Response Theory)** en lugar de Teoría Clásica de Tests:

**Ventajas de IRT:**
- Ajusta por dificultad de cada ítem específico
- Permite comparación entre diferentes versiones del examen
- Produce medidas más precisas en todo el rango de habilidad

**Transformación a escala estandarizada:**
```
Puntaje estandarizado = (Puntaje IRT - Media) / DE × σ_deseada + μ_deseada

Donde:
μ_deseada = 10.0
σ_deseada = 1.0
```

### 3. Niveles de desempeño

Para algunos módulos (especialmente Inglés), además del puntaje numérico se asigna un nivel:

**Inglés:**
- **A-:** Por debajo de A1 (< 35 puntos brutos aprox.)
- **A1:** Usuario básico (35-50 puntos)
- **A2:** Usuario básico avanzado (51-65 puntos)
- **B1:** Usuario independiente (66-80 puntos) ← **Mi nivel**
- **B2:** Usuario independiente avanzado (>80 puntos)

---

## 📈 Cálculo de Quintiles

### Metodología

Los quintiles se calculan **separadamente para cada grupo de referencia**:

1. Se ordenan todos los puntajes del grupo de menor a mayor
2. Se divide la distribución en 5 partes iguales (20% cada una)
3. Se asigna el quintil correspondiente a cada estudiante

**Ejemplo con n=100 estudiantes:**
- Q1: Puestos 1-20 (bottom 20%)
- Q2: Puestos 21-40
- Q3: Puestos 41-60
- Q4: Puestos 61-80
- Q5: Puestos 81-100 (top 20%)

### Grupos de referencia en mi examen (2015)

| Grupo | N estudiantes | Descripción |
|-------|---------------|-------------|
| **Ingeniería** | ~44,063 | Todos los programas de ingeniería |
| **Nacional** | ~216,501 | Todos los programas del país |
| **Ingeniería Industrial** | ~10,849 | Solo Ingeniería Industrial |

**Nota:** Los quintiles de Comunicación Escrita usan n=43,932 debido a criterios de validación específicos.

---

## 🔍 Validez y Confiabilidad

### Validez de constructo

El ICFES realiza estudios regulares para asegurar que los módulos miden lo que pretenden:

- **Comunicación Escrita:** Correlación con muestras de escritura real (r ≈ 0.6-0.7)
- **Razonamiento Cuantitativo:** Correlación con desempeño en matemáticas (r ≈ 0.7-0.8)
- **Lectura Crítica:** Correlación con comprensión académica (r ≈ 0.6-0.7)

### Confiabilidad (Alpha de Cronbach)

Consistencia interna típica de los módulos:

| Módulo | α típico | Interpretación |
|--------|----------|----------------|
| Razonamiento Cuantitativo | 0.80-0.85 | Alta |
| Pensamiento Científico | 0.82-0.87 | Alta |
| Lectura Crítica | 0.75-0.80 | Aceptable-Alta |
| Inglés | 0.88-0.92 | Muy alta |
| Competencias Ciudadanas | 0.70-0.75 | Aceptable |
| Comunicación Escrita | 0.75-0.82 | Alta (inter-rater) |

### Error estándar de medición (SEM)

Estimación del SEM para cada módulo:

```
SEM = σ × √(1 - α)
```

Para σ=1.0 y α típico de 0.80:
```
SEM ≈ 1.0 × √(1 - 0.80) = 0.45
```

**Interpretación:** El "verdadero" puntaje de un individuo probablemente está dentro de ±0.9 puntos (2×SEM, intervalo 95%) del puntaje observado.

---

## ⚖️ Equidad y Sesgo

### Control de sesgo en ítems

El ICFES implementa procedimientos para detectar y eliminar ítems con **Differential Item Functioning (DIF)**:

- Análisis por género
- Análisis por región geográfica
- Análisis por tipo de institución (pública vs privada)
- Análisis por estrato socioeconómico

**Objetivo:** Asegurar que las diferencias en puntajes reflejen diferencias reales de competencia, no artefactos de medición.

### Limitaciones conocidas

A pesar de controles, persisten algunas fuentes de inequidad:

1. **Acceso diferencial a preparación:** Estudiantes de estratos altos tienen mayor acceso a cursos de preparación
2. **Familiaridad con formato:** La experiencia con pruebas estandarizadas influye en desempeño
3. **Ansiedad ante exámenes:** Afecta desproporcionadamente a algunos grupos
4. **Sesgo lingüístico:** Favorece a hablantes nativos de español estándar

---

## 📚 Comparabilidad entre años

### Anclaje estadístico (Equating)

El ICFES utiliza técnicas de **equiparación** para mantener comparabilidad:

1. **Ítems ancla:** Algunos ítems se repiten entre versiones
2. **Análisis de dificultad:** Se ajustan puntajes según dificultad de cada versión
3. **Muestras de referencia:** Se mantienen distribuciones estables año a año

**Limitación:** La comparación directa entre años distantes (>5 años) debe hacerse con cautela debido a:
- Cambios curriculares en programas
- Evolución de estándares educativos
- Cambios en composición de población evaluada

---

## 🎓 Uso apropiado de resultados

### Lo que las instituciones DEBEN hacer

✅ Usar resultados para **diagnóstico agregado** de programas  
✅ Identificar áreas curriculares que requieren fortalecimiento  
✅ Comparar tendencias longitudinales dentro de la institución  
✅ Complementar con otras fuentes de evaluación  

### Lo que las instituciones NO DEBEN hacer

❌ Usar puntajes individuales como **único criterio** de graduación  
❌ Ranking público de estudiantes individuales  
❌ Atribuir todo el resultado a calidad docente (múltiples factores influyen)  
❌ Comparaciones simplistas entre instituciones sin ajustar por contexto  

### Uso en selección laboral

**Recomendación del ICFES:**
- Los resultados pueden ser **un** criterio de selección, nunca el único
- Deben contextualizarse con el programa específico y año de presentación
- No son predictores perfectos de desempeño laboral (correlación moderada)

---

## 📖 Marco Teórico de Competencias

### Definición de competencia (ICFES)

> "Un saber hacer flexible que puede actualizarse en distintos contextos, es decir, como la capacidad de usar los conocimientos en situaciones distintas de aquellas en las que se aprendieron."

### Estructura de las competencias evaluadas

Cada módulo evalúa tres componentes:

1. **Conocimientos:** Conceptos y teorías fundamentales
2. **Habilidades:** Procedimientos y técnicas específicas
3. **Disposiciones:** Actitudes y valores relacionados

**Ejemplo - Razonamiento Cuantitativo:**
- **Conocimiento:** Conceptos matemáticos (álgebra, geometría, estadística básica)
- **Habilidad:** Interpretar gráficos, calcular, estimar órdenes de magnitud
- **Disposición:** Perseverancia ante problemas complejos, precisión

---

## 🌐 Contexto internacional

### Comparación con otros sistemas

| País | Examen equivalente | Características |
|------|-------------------|-----------------|
| **EE.UU.** | GRE (Graduate Record Exam) | Más orientado a posgrado, escala 130-170 |
| **Brasil** | ENADE | Similar a SABER PRO, aplicado al final |
| **México** | EGEL (Ceneval) | Por áreas profesionales específicas |
| **España** | EIR/MIR | Solo para algunas profesiones (salud) |

**Particularidad de SABER PRO:**
- Obligatorio para graduación (requisito legal)
- Combina competencias genéricas (universales) con específicas (por programa)
- Escala estandarizada facilita comparación nacional

---

## 📞 Información Oficial

### Recursos ICFES

- **Portal oficial:** [https://www.icfes.gov.co](https://www.icfes.gov.co)
- **Guías de orientación:** Disponibles por módulo y programa
- **Marco de referencia:** Documentos técnicos sobre construcción de pruebas
- **Resultados históricos:** Reportes agregados por institución y programa

### Consulta de resultados individuales

- Los estudiantes pueden descargar su reporte individual desde el portal ICFES
- Código de registro único (como EK201532097061) permite verificación
- Resultados se conservan en bases de datos ICFES indefinidamente

---

## ⚠️ Advertencias Metodológicas

### Lo que los puntajes NO representan

1. **No son notas sobre 15 o 20:** Es una escala estandarizada con media=10
2. **No miden "inteligencia general":** Evalúan competencias específicas aprendidas
3. **No son estáticos:** Una persona puede mejorar significativamente con preparación
4. **No capturan todas las dimensiones:** Creatividad, liderazgo, ética no están evaluadas

### Interpretación responsable

📌 **Principio clave:** Los resultados deben interpretarse dentro de su marco metodológico, reconociendo tanto su utilidad como sus limitaciones.

---

**Última actualización:** Octubre 2025  
**Fuentes:**  
- ICFES. (2015). *Guía de Orientación SABER PRO*
- ICFES. (2016). *Marco de Referencia para la Evaluación*
- Documentación técnica oficial ICFES

---

*Este documento es un resumen interpretativo con fines educativos. Para información oficial completa, consultar directamente las publicaciones del ICFES.*