import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import scipy.io.wavfile as wav
import librosa

# ======================================================
# 1. CARGAR O GENERAR AUDIO DE ENTRADA (Música/Complejo)
# ======================================================
fs = 48000
duration = 2.0  # 2 segundos de procesado
t_eval = np.linspace(0, duration, int(fs * duration))

# Generamos una señal compleja: Acorde de frecuencias (Bajos + Medios)
# Simula una línea de bajo (60 Hz) + un acorde (220 Hz y 440 Hz)
f_bajo = 60.0
f_medio1 = 220.0
f_medio2 = 440.0

audio_entrada = (0.6 * np.sin(2 * np.pi * f_bajo * t_eval) + 
                 0.3 * np.sin(2 * np.pi * f_medio1 * t_eval) + 
                 0.1 * np.sin(2 * np.pi * f_medio2 * t_eval))

# Guardamos la entrada limpia para comparar
wav.write("Entrada_Musica_Limpia.wav", fs, np.int16(audio_entrada / np.max(np.abs(audio_entrada)) * 32767))

# ======================================================
# 2. PARÁMETROS DEL ICOA 12 Y ECUACIONES DIFERENCIALES
# ======================================================
Re = 6.2; Le = 0.001; Mms = 0.045; Rms = 2.5; K0 = 1500.0; Bl0 = 12.0
alpha_Bl = 15000.0   # No-linealidad agresiva
beta_K = 30000.0

# Voltaje de entrada escalado para forzar la saturación
V_peak = 22.0  
u_in_array = audio_entrada * V_peak

# Función de interpolación para la señal de entrada en el solver continuo
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
print("Procesando señal compleja a través del modelo físico del ICOA 12...")
solucion = solve_ivp(sistema_altavoz, [0, duration], [0.0, 0.0, 0.0], t_eval=t_eval, method='RK45')

v_vel = solucion.y[1]
aceleracion = np.gradient(v_vel, t_eval) # Presión acústica final

# Guardamos el audio procesado
audio_salida = aceleracion / np.max(np.abs(aceleracion))
wav.write("Salida_Musica_Procesada_ICOA12.wav", fs, np.int16(audio_salida * 32767))

print("¡Procesado completado! Escucha 'Salida_Musica_Procesada_ICOA12.wav'")

# ======================================================
# 4. COMPARATIVA ESPECTRAL (INTERMODULACIÓN)
# ======================================================
D_in = np.abs(librosa.stft(audio_entrada))
D_out = np.abs(librosa.stft(audio_salida))
freqs = librosa.fft_frequencies(sr=fs)

plt.figure(figsize=(11, 5))
plt.semilogx(freqs, librosa.amplitude_to_db(np.mean(D_in, axis=1), ref=np.max), label="Entrada Limpia (Mezcla 60Hz + 220Hz + 440Hz)", color='blue')
plt.semilogx(freqs, librosa.amplitude_to_db(np.mean(D_out, axis=1), ref=np.max), label="Salida ICOA 12 (Distorsión de Intermodulación)", color='red', alpha=0.8)
plt.xlim(30, 8000)
plt.ylim(-60, 5)
plt.title("Efecto del Altavoz en Señales Complejas: Distorsión de Intermodulación (IMD)")
plt.xlabel("Frecuencia [Hz]")
plt.ylabel("Magnitud [dB]")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()