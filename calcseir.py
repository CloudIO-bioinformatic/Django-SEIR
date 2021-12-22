#############################################################################################################
#### Proyecto creado por Claudio Quevedo Gallardo, estudiante de Ing. Civil en Bioinformática, Utal 2020.####
#33##########################################################################################################

import numpy as np
from scipy.integrate import odeint
import pandas as pd
import pymongo
from pymongo import MongoClient
import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
import re

client = MongoClient('localhost',27017)
db = client['SEIR']
#comunas = db['comunas']
principal_comuna = db['principal_comuna']
principal_listacomunas = db['principal_listacomunas']
principal_listaregiones = db['principal_listaregiones']
principal_estadisticas = db['principal_estadisticas']
#se borra la bd para que no haya duplicamiento en el testeo de codigo
#db.drop()
client.drop_database('SEIR')

#lectura de set de datos
datasets = pd.read_csv('output/datos_final.ready',sep='\t')
records = []
for i in range(0, 345):
    records.append([datasets.values[i,j] for j in range(0, 7)])
#region,comuna,poblacion, infectado, fallecido, recuperado, migracion


# The SIR model differential equations.
def deriv(y, t, N, beta, gamma, mu):
    S, E, I, R = y
    #print (S)
    #mu * S, si hay un transito entre comunas de forma normal, pero supondremos que 1 de cada 1000 personas lo esta haciendo
    dSdt = -beta * S * I / N  - ( mu * S ) / 1000
    dEdt = beta * S * I / N - ( sigma + mu / 1000 ) * E
    dIdt = sigma * E - ( gamma + mu / 1000 ) * I
    dRdt = gamma * I - ( mu / 1000 ) * R
    return dSdt, dEdt, dIdt, dRdt

#for data in records[:2]:
for data in records:
    # Total population, N.
    N = data[2]
    # Initial number of infected and recovered individuals, I0 and R0.
    I0, R0 = data[3], data[5]
    # Everyone else, S0, is susceptible to infection initially.
    S0 = N - I0 - R0
    E0 = 0
    # Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
    sigma, gamma, rho, mu, alpha, kappa, d = 1./5, 1./14, 2.35, data[6], 0.25, 396, data[4]
    beta0 = gamma * ( rho / ( sigma / sigma + mu ) )
    beta = beta0 * (1 - alpha) * (1 - (d / N))**kappa
    # A grid of time points (in days)
    days = 365
    t = np.linspace(0, days, days)
    # Initial conditions vector
    y0 = S0, E0, I0, R0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma, mu))
    S, E, I, R = ret.T
    print("SEIR calculado para: ",data[1])
    today = date.today()
    regionregexp = re.sub('_',' ',data[0])
    a = principal_listacomunas.insert_one({'region':regionregexp,'nombre':data[1]}).inserted_id

    region = principal_listaregiones.find_one({'nombre': regionregexp})

    if not region:
        r = principal_listaregiones.insert_one({'nombre':regionregexp}).inserted_id
    #comuna = db[data[1]]
    for day in range(0,days):
        b = principal_comuna.insert_one({'date':str(today),'region':regionregexp,'comuna':data[1],'dia':day,'S':S[day],'E':E[day],'I':I[day],'R':R[day]}).inserted_id
    max_infectados = principal_comuna.find_one({'comuna':data[1]},sort=[("I", -1)])
    max_dia = max_infectados['dia']
    proxdate = today + timedelta(days=max_dia)
    max_S = round(max_infectados['S'])
    max_E = round(max_infectados['E'])
    max_I = round(max_infectados['I'])
    max_R = round(max_infectados['R'])

    c = principal_estadisticas.insert_one({'poblacion_porcentaje':round((max_I/data[2])*100, 3),'poblacion':round(data[2]),'comuna':data[1],'maxS':max_S,'maxE':max_E,'maxI':max_I,'maxR':max_R,'maxDia':max_dia,'dia':str(proxdate)}).inserted_id
#region = principal_listaregiones.find({})
#for a in region:
#    print(a)
#for comuna in db.Calama.find_one({'dia': 200}):
#        pprint.pprint(comuna)

#OBTENER LO QUE BUSCO
#oo = db.Calama.find_one({'dia': 200})
#print(oo)
#max = db.Calama.find_one(sort=[("S", -1)])
#print(max)
