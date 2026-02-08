import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
from scipy.stats import norm
import math

SIM_TIME_LIMIT = 10000 # seconds
REPETITIONS = 5
N = 45 # Numero di Server

data_fase_1 = np.loadtxt("results/fase1.data")

print("-----UTILIZZO-----")
print(f"N = {N}")
print(f"Ripetizioni per configurazione = {REPETITIONS}")
print("------------------")

# --- COSTO DI NOLEGGIO FISSO ---
def compute_rental_cost_comparison(cost_per_hour1, cost_per_hour2, n = N):
    """Calcola il costo basato solo sul numero di server affittati """
    costo_fisso1 = n * cost_per_hour1
    costo_fisso2 = n * cost_per_hour2
    print(f"Costo Noleggio Fisso Tipo 1 (N={n}) -> {costo_fisso1:.2f}$/hour")
    print(f"Costo Noleggio Fisso Tipo 2 (N={n}) -> {costo_fisso2:.2f}$/hour")
    return costo_fisso1, costo_fisso2

def compute_rental_cost(cost_per_hour, n = N):
    """Calcola il costo basato solo sul numero di server affittati """
    costo_fisso = n * cost_per_hour
    print(f"Costo Noleggio Fisso Tipo  (N={n}) -> {costo_fisso:.2f}$/hour")
    return costo_fisso

# --- COSTO OPERATIVO DURANTE IL TEMPO DI SIMULAZIONE (Basato sull'utilizzo busy_percentage) ---
def compute_cost_comparison(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 -> {(costo_totale1 * n):.2f}")
    print(f"Costo totale 2 -> {(costo_totale2 * n):.2f}") 

def compute_cost(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale -> {costo_totale * n:.2f}")

#---COSTO OPERATIVO IN UN ORA (Basato sull'utilizzo busy_percentage)---
def compute_cost_comparison_hour(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 in un ora -> {((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour")
    print(f"Costo totale 2 in un ora -> {((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour") 

def compute_cost_hour(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale in un ora -> {(costo_totale / SIM_TIME_LIMIT) * 3600 * n:.2f}$/hour")


#---CALCOLO CI---
#n_repeat è il numero di run per configurazione
def compute_CI(std, confidence_percentage,label=""):
    df = REPETITIONS - 1
    alpha = 1 - (confidence_percentage / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std / math.sqrt(REPETITIONS))
    return print(f"CI_{label} -> +-{(ic):.8f}")

std = data_fase_1[1]


compute_CI(std=std, confidence_percentage=65)
