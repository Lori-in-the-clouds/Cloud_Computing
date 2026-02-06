#!/usr/bin/python3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib as mpl
import matplotlib.colors as mc
from plot import plot_line, set_fonts

lam=200 #MODIFICA
cv=1.0  #MODIFICA

"""
cv = 1.0 se il tempo di servizio è esponenziale
cv = 0.0 determinstico
"""

#Utilizzata per calcolare il tempo di risposta medio atteso
def theoretical(N, mu):
    rho=lam/(mu * N)
    if rho >= 1:
        return None
    else:
        return 1/mu * (1 + ((1+cv**2)/2)*rho/(1-rho)) 
    
data_mu1 = np.loadtxt("results/fase_2_mu1.data") #MODIFICA
data_mu2 = np.loadtxt("results/fase_2_mu2.data") #MODIFICA

N_mu1 = data_mu1[:,0] 
N_mu2 = data_mu2[:,0]

life_time_mu1 = data_mu1[:,1]
life_time_mu2 = data_mu2[:,1]

#Per ricavare il CI
data_ci_mu1 = np.loadtxt("results/ic_mu1_err.data") #MODIFICA
data_ci_mu2 = np.loadtxt("results/ic_mu1_err.data") #MODIFICA

ic_mu1 = data_ci_mu1[:,1]
ic_mu2 = data_ci_mu2[:,1]


if __name__ == "__main__":
    print(f"Configurazione con lambda = {lam} e cv = {cv}")
    # plot respone time
    fig, ax = plt.subplots()
    ax.set(xlabel='Number of servers N', ylabel='Time [s]')
    #plot_line(ax, 'o--', 'sample.data', 'Response Time', '#x', 'y', 'sigma(y)')
    
    # Inserisci il range dei possibili valori di N (ricordati che range esclude l'ultimo valore)
    range_N_1 =list(range(30, 56)) #MODIFICA
    range_N_2 =list(range(15, 56)) #MODIFICA
    mu_1 = 8 #MODIFICA
    mu_2 = 16 #MODIFICA

    plot_line(ax, '-', None, f'Theoretical curve $\mu$={mu_1}', range_N_1, [theoretical(x,mu= mu_1) for x in range_N_1])
    plot_line(ax, '-', None, f'Theoretical curve $\mu$={mu_2}', range_N_2, [theoretical(x,mu= mu_2) for x in range_N_2])

    #Inserisci prima asse x e poi asse y (RIMUOVI IC_MU SE NON LO UTILIZZI)
    plot_line(ax, 'o--', None, f'Response time $\mu$={mu_1}', N_mu1, life_time_mu1,ic_mu1)
    plot_line(ax, 'o--', None, f'Response time $\mu$={mu_2}', N_mu2, life_time_mu2,ic_mu2)

    #Per settare il range di valori nell'asse Y
    ax.set_ylim(0, 1)

    #Per settare una linea orizzontale rossa 
    ax.axhline(y=0.250, color='red', linestyle='-', linewidth=1) #MODIFICA
    
    plt.legend()
    plt.show()
    #plt.savefig('sample.png')