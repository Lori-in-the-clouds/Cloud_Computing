#!/usr/bin/python3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib as mpl
import matplotlib.colors as mc
from plot import plot_line, set_fonts

lam=100 #MODIFICA
cv=3.0  #MODIFICA

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
    
data = np.loadtxt("results/fase2.data") 


N_data = data[:,0] 
life_time = data[:,1]

#Per ricavare il CI
data_ci = np.loadtxt("results/ic_err.data")
ic = data_ci[:,1]



if __name__ == "__main__":
    print(f"Configurazione con lambda = {lam} e cv = {cv}")
    # plot respone time
    fig, ax = plt.subplots()
    ax.set(xlabel='Number of servers N', ylabel='Time [s]')
    #plot_line(ax, 'o--', 'sample.data', 'Response Time', '#x', 'y', 'sigma(y)')
    
    # Inserisci il range dei possibili valori di N (ricordati che range esclude l'ultimo valore)
    range_N = [15, 20, 25, 30, 35, 40, 45, 50]

    range_N_for_theoretical = list(range(15, 51)) #MODIFICA

    plot_line(ax, '-', None, f'Theoretical curve', range_N_for_theoretical, [theoretical(x,mu= 10) for x in range_N_for_theoretical])


    #Inserisci prima asse x e poi asse y (RIMUOVI IC_MU SE NON LO UTILIZZI)
    plot_line(ax, 'o--', None, f'Response time', range_N, life_time,ic * 2)
    #N.B. La funzione ti richide tutto l'intervallo di certezza, quindi l'IC devi moltiplicarlo per 2

    #Per settare il range di valori nell'asse Y
    ax.set_ylim(0, 1.1)
    #Per settare i valori sull'asse Y
    #ax.set_yticks([0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])

    #Per settare una linea orizzontale rossa 
    ax.axhline(y=0.250, color='red', linestyle='-', linewidth=1) #MODIFICA
    
    plt.legend()
    plt.savefig('sample.png')
    plt.show()