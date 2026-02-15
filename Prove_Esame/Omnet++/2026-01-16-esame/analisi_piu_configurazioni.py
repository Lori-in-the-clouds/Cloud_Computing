import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import math

SIM_TIME_LIMIT = 10000 # seconds
REPETITIONS = 5
N = 45 # Numero di Server

#---COSTO DEL SISTEMA DURANTE IL PERIODO DI SIMULAZIONE (considerando N server)--
def compute_cost_comparison(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 -> {(costo_totale1 * n):.2f}")
    print(f"Costo totale 2 -> {(costo_totale2 * n):.2f}") 
    return costo_totale1, costo_totale2

def compute_cost(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale -> {costo_totale * n:.2f}")
    return costo_totale

#---COSTO DEL SISTEMA IN UN ORA (considerando N server)---
def compute_cost_comparison_hour(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 in un ora -> {((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour")
    print(f"Costo totale 2 in un ora -> {((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour") 
    return ((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n), ((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n)

def compute_cost_hour(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale in un ora -> {(costo_totale / SIM_TIME_LIMIT) * 3600 * n:.2f}$/hour")
    return ((costo_totale / SIM_TIME_LIMIT) * 3600 * n)

#n_repeat è il numero di run per configurazione
def compute_CI(std, confidence_percentage,label=""):
    df = REPETITIONS - 1
    alpha = 1 - (confidence_percentage / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std / math.sqrt(REPETITIONS))
    print(f"CI_{label} -> +-{(ic):.8f}")
    return ic

print("server 1".center(50, "="))

data = np.loadtxt("results/fase_2.data")
list_ic_costo = []

for row in range(data.shape[0]):
    row_data = data[row,:]

    tr_1 = row_data[1]
    std_1 = row_data[2]
    
    tr_2 = row_data[3]
    std_2 = row_data[4]
    
    tr_g = row_data[5]
    std_g = row_data[6]

    ic_1 = compute_CI(std_1,65,label=str("ic_1"))
    ic_2 = compute_CI(std_2,65,label=str("ic_2"))
    ic_g = compute_CI(std_g,65,label=str("ic_g"))


    #Per salvare i valori di N, IC e costo in un file
    list_ic_costo.append([ic_1,ic_2,ic_g])   

#Per salvare i valoir di N, IC e costo in un file    
np.savetxt("results/ic_mu1_err.data", list_ic_costo, header="IC_1\tIC_2\tIC_g", fmt=['%.5f', '%.5f', '%.5f'])


