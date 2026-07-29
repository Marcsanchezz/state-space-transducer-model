# 🔊 Non-Linear Electro-Dynamic Transducer Simulation (State-Space Model)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Domain](https://img.shields.io/badge/Domain-Audio%20DSP%20%26%20Acoustics-orange)

Prototipo de simulación física y electromecánica de un altavoz de alta potencia en régimen de alta excursión. El modelo resuelve mediante el método de integración **Runge-Kutta (RK45)** el sistema de ecuaciones diferenciales acopladas, considerando la caída del campo magnético $Bl(x)$ y el endurecimiento de la suspensión $K_{ms}(x)$.

---

## 📸 Resultados de Simulación

| Excursión vs Corriente | Caída del Campo Magnético $Bl(x)$ |
| :---: | :---: |
| ![Excursión](assets/1_excursion_corriente.png) | ![Bl(x)](assets/2_curva_Bl_x.png) |

---

## ⚡ Estructura del Proyecto

```text
.
├── assets/                       # Gráficas en alta resolución para informes
│   ├── 1_excursion_corriente.png
│   └── 2_curva_Bl_x.png
├── modelo_fisico_icoa12.py       # Solucionador principal en Espacio de Estados
├── procesar_cancion_icoa12.py    # Procesador de transitorios y archivos de audio
├── generar_assets.py             # Script de generación de métricas y gráficos
├── Dossier_Tecnico.md            # Informe técnico detallado
└── README.md                     # Documentación principal