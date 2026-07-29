import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os

# 1. Crear carpeta de salida
os.makedirs("assets", exist_ok=True)

# 2. Configuración Física
fs = 48000
duration = 1.0
t_eval = np.linspace(0, duration, int(fs * duration))
f0 = 80.0 # Hz
V_peak = 20.0 # Voltios (Saturación)

u_in = lambda t: V_peak * np.sin(2 * np.pi * f0 * t)

# Parámetros Thiele-Small + No linealidades
Re = 6.2; Le = 0.0012; Mms = 0.045; Rms = 2.5; K0 = 1500.0; Bl0 = 12.0
alpha_Bl = 15000.0; beta_K = 30000.0

def sistema_altavoz(t, y):
    x, v, i = y
    Bl_x = max(Bl0 * (1.0 - alpha_Bl * (x**2)), 0.1)
    Kms_x = K0 * (1.0 + beta_K * (x**2))
    return [v, (Bl_x * i - Rms * v - Kms_x * x) / Mms, (u_in(t) - Re * i - Bl_x * v) / Le]

# 3. Resolver
sol = solve_ivp(sistema_altavoz, [0, duration], [0.0, 0.0, 0.0], t_eval=t_eval, method='RK45')
x_pos, v_vel, i_cor = sol.y
aceleracion = np.gradient(v_vel, t_eval)

# Estilo gráfico profesional para el Dossier
plt.style.use('seaborn-v0_8-paper' if 'seaborn-v0_8-paper' in plt.style.available else 'default')

# FIGURA 1: Excursión Física vs Corriente
fig, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(t_eval[:1000] * 1000, x_pos[:1000] * 1000, 'b-', label='Excursión x(t) [mm]')
ax1.set_xlabel('Tiempo [ms]')
ax1.set_ylabel('Excursión [mm]', color='b')
ax2 = ax1.twinx()
ax2.plot(t_eval[:1000] * 1000, i_cor[:1000], 'r--', label='Corriente i(t) [A]')
ax2.set_ylabel('Corriente [A]', color='r')
plt.title("Respuesta Electromecánica No Lineal (Excursión vs Corriente)")
plt.grid(True)
plt.savefig("assets/1_excursion_corriente.png", dpi=300, bbox_inches='tight')
plt.close()

# FIGURA 2: Curva de Caída de Bl(x)
x_range = np.linspace(-0.008, 0.008, 500) # -8mm a +8mm
Bl_curve = [max(Bl0 * (1.0 - alpha_Bl * (x**2)), 0.1) for x in x_range]
plt.figure(figsize=(7, 3.5))
plt.plot(x_range * 1000, Bl_curve, 'g-', linewidth=2)
plt.axvline(0, color='gray', linestyle='--')
plt.title("Caída del Factor de Fuerza Bl(x) por Excursión de la Bobina")
plt.xlabel("Posición del Cono x [mm]")
plt.ylabel("Bl [T·m]")
plt.grid(True)
plt.savefig("assets/2_curva_Bl_x.png", dpi=300, bbox_inches='tight')
plt.close()

print("✅ Gráficas HD guardadas correctamente en la carpeta /assets")