import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import scipy.io.wavfile as wav
import librosa

# ======================================================
# 1. CARGAR TU CANCIÓN / AUDIO REAL
# ======================================================
# PON AQUÍ EL NOMBRE DE TU ARCHIVO DE AUDIO (Ej: "cancion.wav" o "musica.mp3")
# Si no existe, el script generará un patrón de batería/bombo real para probar los transitorios
archivo_usuario = "cancion.wav" 

fs = 48000
duration = 4.0  # Procesamos 4 segundos para no saturar la CPU

try:
    print(f"Cargando archivo {archivo_usuario}...")
    y_audio, sr = librosa.load(archivo_usuario, sr=fs, duration=duration, mono=True)
    print("¡Canción cargada con éxito!")
except:
    print("No se encontró archivo propio. Generando impacto de BOMBOS/TRANSITORIOS de prueba...")
    t_dummy = np.linspace(0, duration, int(fs * duration))
    # Generar un ritmo con transitorios marcados (Bombo a 60Hz cayendo en frecuencia)
    y_audio = np.zeros_like(t_dummy)
    for kick_time in [0.5, 1.5, 2.5, 3.5]:
        idx = int(kick_time * fs)
        dur_kick = int(0.2 * fs)
        t_k = np.linspace(0, 0.2, dur_kick)
        env = np.exp(-30 * t_k) # Envolvente de ataque rápido
        freq_decay = 120 * np.exp(-40 * t_k) + 40
        y_audio[idx:idx+dur_kick] += np.sin(2 * np.pi * freq_decay * t_k) * env

# Normalizamos entrada
y_audio = y_audio / np.max(np.abs(y_audio))
t_eval = np.linspace(0, duration, len(y_audio))

# Guardamos la entrada limpia
wav.write("1_Cancion_Original_Limpia.wav", fs, np.int16(y_audio * 32767))

# ======================================================
# 2. ECUACIONES DIFERENCIALES DEL ICOA 12 (Ataque a Transitorios)
# ======================================================
Re = 6.2; Le = 0.0012; Mms = 0.050; Rms = 3.0; K0 = 1600.0; Bl0 = 12.5
alpha_Bl = 18000.0   # Saturación fuerte de excursión
beta_K = 35000.0

V_peak = 25.0  # Voltaje alto para forzar la compresión del transitorio
u_in_array = y_audio * V_peak

def u_in(t):
    idx = int(t * fs)
    if idx >= len(u_in_array): idx = len(u_in_array) - 1
    return u_in_array[idx]

def sistema_altavoz(t, y):
    x, v, i = y
    Bl_x = max(Bl0 * (1.0 - alpha_Bl * (x**2)), 0.1)
    Kms_x = K0 * (1.0 + beta_K * (x**2))
    
    dxdt = v
    dvdt = (Bl_x * i - Rms * v - Kms_x * x) / Mms
    didt = (u_in(t) - Re * i - Bl_x * v) / Le
    return [dxdt, dvdt, didt]

# ======================================================
# 3. RESOLUCIÓN DE LA FÍSICA
# ======================================================
print("Simulando respuesta física del cono a los transitorios de la canción...")
solucion = solve_ivp(sistema_altavoz, [0, duration], [0.0, 0.0, 0.0], t_eval=t_eval, method='RK45')

v_vel = solucion.y[1]
aceleracion = np.gradient(v_vel, t_eval)

# Guardamos la canción procesada
audio_salida = aceleracion / np.max(np.abs(aceleracion))
wav.write("2_Cancion_Procesada_ICOA12.wav", fs, np.int16(audio_salida * 32767))

print("--------------------------------------------------")
print("¡Procesado completado!")
print("Escucha '1_Cancion_Original_Limpia.wav' vs '2_Cancion_Procesada_ICOA12.wav'")
print("--------------------------------------------------")

# ======================================================
# 4. VISUALIZACIÓN DEL ATAQUE DE TRANSITORIOS
# ======================================================
plt.figure(figsize=(12, 6))
plt.plot(t_eval[:int(fs*1.5)], y_audio[:int(fs*1.5)], label="Canción Original (Transitorios Afilados)", color='blue', alpha=0.6)
plt.plot(t_eval[:int(fs*1.5)], audio_salida[:int(fs*1.5)], label="Salida ICOA 12 (Transitorio Comprimido por Masa/Inercia)", color='red', alpha=0.8)
plt.title("Aplastamiento de Transitorios por la Masa Móvil y la Suspensión del Altavoz")
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud Normalizada")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()