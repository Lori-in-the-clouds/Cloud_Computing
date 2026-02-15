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
    
data = np.loadtxt("results/fase_2.data") #MODIFICA


p = data[:,0] 
tr_1 = data[:,1]
tr_2 = data[:,3]
tr_g = data[:,5]


#Per ricavare il CI
data_ci = np.loadtxt("results/ic_mu1_err.data")


ic_1 = data_ci[:,0]
ic_2 = data_ci[:,1]
ic_g = data_ci[:,2]

if __name__ == "__main__":
    print(f"Configurazione con lambda = {lam} e cv = {cv}")
    # plot respone time
    fig, ax = plt.subplots()
    ax.set(xlabel='Number of servers N', ylabel='Time [s]')
    #plot_line(ax, 'o--', 'sample.data', 'Response Time', '#x', 'y', 'sigma(y)')
    
    # Inserisci il range dei possibili valori di N (ricordati che range esclude l'ultimo valore)
    range_N_1 =list(range(30, 56)) #MODIFICA
    range_N_2 =list(range(15, 56)) #MODIFICA


    #Inserisci prima asse x e poi asse y (RIMUOVI IC_MU SE NON LO UTILIZZI)
    plot_line(ax, 'o--', None, f'Response time 1', p, tr_1,ic_1 * 2)
    plot_line(ax, 'o--', None, f'Response time 2', p, tr_2,ic_2 * 2)
    plot_line(ax, 'o--', None, f'Response time Global', p, tr_g,ic_g * 2)
    #N.B. La funzione ti richide tutto l'intervallo di certezza, quindi l'IC devi moltiplicarlo per 2

    #Per settare il range di valori nell'asse Y
    ax.set_ylim(0, 0.5)
    ax.set_xlim(0, 0.5)
    #Per settare i valori sull'asse Y
    #ax.set_yticks([0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])

    plt.legend()
    plt.savefig('sample.png')
    plt.show()