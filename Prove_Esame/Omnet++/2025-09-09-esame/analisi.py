import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
from scipy.stats import norm
import math

SIM_TIME_LIMIT = 1000 # seconds
REPETITIONS = 10
N = 45 # Numero di Server

data_mu1 = np.loadtxt("results/fase_1_mu1.data")
data_mu2 = np.loadtxt("results/fase_1_mu2.data")

print("-----UTILIZZO-----")
print(f"N = {N}")
print(f"Ripetizioni per configurazione = {REPETITIONS}")
print("------------------")

#---COSTO DEL SISTEMA DURANTE IL PERIODO DI SIMULAZIONE (considerando N server)--
def compute_cost_comparison(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 -> {(costo_totale1 * n):.2f}")
    print(f"Costo totale 2 -> {(costo_totale2 * n):.2f}") 

def compute_cost(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale -> {costo_totale * n:.2f}")

#---COSTO DEL SISTEMA IN UN ORA (considerando N server)---
def compute_cost_comparison_hour(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 in un ora -> {((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour")
    print(f"Costo totale 2 in un ora -> {((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour") 

def compute_cost_hour(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale in un ora -> {(costo_totale / SIM_TIME_LIMIT) * 3600 * n:.2f}$/hour")

#n_repeat è il numero di run per configurazione
def compute_CI(std, confidence_percentage,label=""):
    df = REPETITIONS - 1
    alpha = 1 - (confidence_percentage / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std / math.sqrt(REPETITIONS))
    return print(f"CI_{label} -> +-{(ic):.8f}")

std_1 = data_mu1[1]
busy_1 = data_mu1[2]

std_2 = data_mu2[1]
busy_2 = data_mu2[2]

compute_CI(std=std_1, confidence_percentage=65,label="mu1")
compute_CI(std=std_2, confidence_percentage=65,label="mu2")

compute_cost_comparison(busy_percentage1=busy_1, busy_percentage2=busy_2, cost_per_hour1=1.5, cost_per_hour2=3)
compute_cost_comparison_hour(busy_percentage1=busy_1, busy_percentage2=busy_2, cost_per_hour1=1.5, cost_per_hour2=3)

