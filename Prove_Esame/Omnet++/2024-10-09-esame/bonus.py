#!/usr/bin/python3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib as mpl
import matplotlib.colors as mc
from plot import plot_line, set_fonts

lam=10 
cv=1.0  
mu = 10
mu_net = 1 / 0.070

"""
cv = 1.0 se il tempo di servizio è esponenziale
cv = 0.0 determinstico
"""

#Utilizzata per calcolare il tempo di risposta medio atteso
def theoretical(f_l):
    # Ramo Local
    # Formula M/M/1: T = 1 / (mu - lambda_locale)
    lambda_l = lam * f_l
    print(lambda_l)
    if lambda_l >= mu: return None # Saturazione
    t_local = 1 / (mu - lambda_l)
    
    # Ramo Cloud (Coda Rete + Delay Server)
    lambda_c = lam * (1 - f_l)
    if lambda_c >= mu_net: return None # Saturazione rete
    t_cloud = (1 / (mu_net - lambda_c)) + (1 / mu)
    
    # Tempo totale medio pesato
    return f_l * t_local + (1 - f_l) * t_cloud
    
data = np.loadtxt("results/fase_2.data") 

f_l = data[:,0] 
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

    #Inserisci prima asse x e poi asse y (RIMUOVI IC_MU SE NON LO UTILIZZI)
    plot_line(ax, 'o--', None, f'Response time', f_l,life_time,[elem * 2 for elem in ic ])
    plot_line(ax, '-', None, f'Theoretical curve',f_l, [theoretical(elem) for elem in f_l])

    #Per settare il range di valori nell'asse Y
    ax.set_ylim(0.15, 1)
    ax.set_yticks([0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])

    #Per settare una linea orizzontale rossa 
    #ax.axhline(y=0.250, color='red', linestyle='-', linewidth=1) #MODIFICA
    
    plt.legend()
    plt.savefig('sample.png')
    plt.show()