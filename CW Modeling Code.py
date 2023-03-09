# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 19:36:04 2022


@author: Nisa
"""

import pandas as pd
import numpy as np
from pandas import ExcelWriter
import math as m
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from Plots_Calib import plots

#read in data from excel 
df = pd.read_excel (r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Hourly_Input.xlsx', sheet_name='Input')

#create arrays from excel data
day= np.asarray(list(df['Day']))
time = np.asarray(list(df['Time']))
P = np.asarray(list(df['Precip(m)']))
temp = np.asarray(list(df['Temp']))
COD_i = np.asarray(list(df['COD'])) 
OrgN_i = np.asarray(list(df['Organic N']))       
NH4_i = np.asarray(list(df['Ammonium']))  
NO3_i = np.asarray(list(df['Nitrate']))   

########## Water Balance Functions ########
#Horizontal flow CW dimensions
HF_width = 0.7874  #m
HF_length = 1.397  #m 
HF_height = 0.4572 #m 
HF_area = HF_width * HF_length #m2 

#Vertical flow CW dimensions
VF_width = 0.6477  #m
VF_length = 0.6477 #m
VF_height = 0.6 #m
VF_area = VF_width * VF_length #m2

#create inflow set the same size as the input data
def VF_Qi(): 
 inflow = 0.001 #m3/hour
 return inflow

#store results in an array
VF_Qi = np.asarray(VF_Qi())
#VF outflow equals VF inflow 
VF_Qo = VF_Qi
#HF inflow equals VF outflow
HF_Qi = VF_Qo

HF_Qo= HF_Qi





#calculate evapotranspiration (m/hour)
def ET():
    #hour
    dl = 1    #hour
    #heat index
    I = 167.1  #C
    a = 6.75*(10**-7)*(I**3)-7.71*(10**-5)*(I**2)+1.792*(10**-2)*I+0.49239 
    #Thortwaite's equation
    ET = 16*dl/12*((10*temp/I)**a)/(30*100)/10
    return ET

#store results in an array
ET = np.asarray(ET()) 

def VF_volume(): 
    #initial water volume
    VF_volume = 0.015                          #m3
    #water balance equation
    dVdt = VF_Qi-VF_Qi+(P*VF_area)-(ET*VF_area)  #m3/day
    #store result in array
    dVdt = np.asarray(dVdt)                      #m3/day
    #volume equals intial plus change each day 
    VF_volume += dVdt                            #m3
    return VF_volume*1000                        #L

def HF_volume(): 
    #initial water volume
    HF_volume = 0.14                           #m3
    #water balance equation
    dVdt = HF_Qi-HF_Qo+(P*HF_area)-(ET*HF_area)  #m3/day
    #store result in array
    dVdt = np.asarray(dVdt)                      #m3
    #volume equals intial plus change each day 
    HF_volume += dVdt                            #m3
    return HF_volume*1000                        #L

#store results in an array
VF_volume = np.asarray(VF_volume())    
HF_volume = np.asarray(HF_volume())
df_VF=pd.DataFrame(VF_volume, index= time)
df_HF=pd.DataFrame(HF_volume, index=time)
df_ET= pd.DataFrame(ET, index=time)



#######Oxygen mass balance########
DO_i = 1.50    #mg/L
T = temp        #avg. temp of water (C)
VF_kR = .5*1.08**(temp-20)/24  # (/hr) #(0-1)
VF_kr=np.asarray(VF_kR)
HF_kR = 0.001*1.08**(temp-20)/24  # (/hr) #(0-1)

#calculate DO saturation
DO_s = 14.652-0.41022*T+0.007991*T**2-0.00007777*T**3 #g/m3

#calculate mass flux 
VF_JO2 = VF_kR*(DO_s-DO_i)


#VF Monod Parameters for heterotrophs
VF_HT_Y = 1.23*1.08**(temp-20)/24
VF_HT_DO_Ks = 1.3*1.08**(temp-20)/24
VF_HT_TOC_Ks = 60*1.08**(temp-20)/24
VF_HT_mu_max = 4*1.08**(temp-20)/24
TOC = COD_i
#VF Monod Parameters for autotrophs
VF_NS_Y = 0.084 *1.08**(temp-20)/24
VF_NS_DO_Ks = 0.7*1.08**(temp-20)/24
VF_NS_NH4_Ks = 1.5*1.08**(temp-20)/24
VF_NS_mu_max = .0005 *1.08**(temp-20)/24

#VF Monod equations
VF_HT_growth = VF_HT_mu_max*(TOC/(TOC+VF_HT_TOC_Ks))*(VF_HT_DO_Ks/(DO_i+VF_HT_DO_Ks))
VF_HT_res = VF_HT_growth/VF_HT_Y
VF_NS_growth = VF_NS_mu_max*(NH4_i/(NH4_i+VF_NS_NH4_Ks))*(DO_i/(DO_i+VF_NS_DO_Ks))
VF_NS_res = VF_NS_growth/VF_NS_Y

#HF Monod Parametersfor heterotrophs
HF_HT_Y = 0.8*1.25**(temp-20)/24
HF_HT_DO_Ks = 2*1.25**(temp-20)/24
HF_HT_TOC_Ks = 40*1.08**(temp-20)/24
HF_HT_mu_max = 12*1.08**(temp-20)/24
TOC = COD_i
#HF Monod Parameters for autotrophs
HF_NS_Y = 0.085/24
HF_NS_DO_Ks = 124/24
HF_NS_NH4_Ks = 1/24
HF_NS_mu_max = .01/24

#HF Monod equations
HF_HT_growth = HF_HT_mu_max*(TOC/(TOC+HF_HT_TOC_Ks))*(HF_HT_DO_Ks/(DO_i+HF_HT_DO_Ks))
HF_HT_res = HF_HT_growth/HF_HT_Y
HF_NS_growth = HF_NS_mu_max*(NH4_i/(NH4_i+HF_NS_NH4_Ks))*(DO_i/(DO_i+HF_NS_DO_Ks))
HF_NS_res = HF_NS_growth/HF_NS_Y

#DO mass balances
VF_DO = DO_i + VF_JO2 - VF_HT_res - VF_NS_res
HF_JO2 = HF_kR*(DO_s-VF_DO)
HF_DO = VF_DO + HF_JO2 - HF_HT_res - HF_NS_res
print(VF_DO, HF_DO)
##############COD mass balance#############

Q = VF_Qi*1000 #L
Qi = Q
Qo = HF_Qo*1000 #L
n= 3   #no of tanks
#Stover-Kincannon Parameters

#VF
VF_k=0.5
VF_kd=VF_k*1.01**(temp-20)
VF_mu_max= 990*1.01**(temp-20)/24*(VF_DO/(VF_kd+VF_DO)) #mg/L-hr (500-3000)
VF_kB= 868   #mg/L-hr (500-2000)
VF_COD1= COD_i-VF_mu_max*COD_i/(VF_kB+Qi*COD_i/VF_volume/n)
VF_COD2= VF_COD1-VF_mu_max*VF_COD1/(VF_kB+Qi*VF_COD1/VF_volume/n)
VF_COD= VF_COD2-VF_mu_max*VF_COD2/(VF_kB+Qi*VF_COD2/VF_volume/n)


VF_COD=np.asarray(VF_COD)
df_VF_COD= pd.DataFrame(VF_COD, columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Comparison\R-squared\VF_Control_COD.xlsx',df_VF_COD,[0,600],200,100)

#HF
HF_k=0.1
HF_kd=HF_k*1.01**(temp-20)
HF_mu_max= 1609*1.01**(temp-20)/24*(HF_DO/(HF_kd+HF_DO)) #mg/L-hr (1500-3000)
HF_kB= 1177     #mg/L-hr (300-1200)

HF_COD1= VF_COD-HF_mu_max*VF_COD/(HF_kB+Qi*VF_COD/HF_volume/n)
HF_COD2= HF_COD1-HF_mu_max*HF_COD1/(HF_kB+Qi*HF_COD1/HF_volume/n)
HF_COD= HF_COD2-HF_mu_max*HF_COD2/(HF_kB+Qi*HF_COD2/HF_volume/n)

HF_COD= np.asarray(HF_COD)
df_HF_COD= pd.DataFrame(HF_COD, columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\HF_Control_COD.xlsx',df_HF_COD,[0,600],200,100)


#=============================================================================
########## Nitrogen Balance Functions #########
########## Nitrogen Balance Functions #########
#Background concentrations (mg/L)
OrgN_0 = 5
NH4_0 = 0     
NO3_0 = 0     
n=3
          
######Rate constants (per day)
VF_k=0.1
VF_kd=VF_k*1.01**(temp-20)
HF_k=0.01
HF_kd=HF_k*1.01**(temp-20)
#plant decomposition
VF_kpd = 0.005*1.04**(temp-20)   #(15-25)
HF_kpd = 0.008*1.04**(temp-20)    #(5-18)

#mineralization
km_a = 0.6*1.08**(temp-20) #aerobic   
km_an = 0.12*1.08**(temp-20) #anaerobic   (0.01,0.09)


#nitrification
kn_a =  0.07*1.08**(temp-20)*(VF_DO/(VF_kd+VF_DO))  #aerobic    (0.5-3)
#vf_kn_an = 0.0000537*1.08**(temp-20) #anaerobic

kn_an =  0.006*1.02**(temp-20)*(HF_DO/(HF_kd+HF_DO))  #aerobic  (0.01,0.15)
#hf_kn_an = 0.01*1.2**(temp-20) #anaerobic

#plant uptake of ammonia 
VF_kpu_NH4 = 0.002*1.08**(temp-20)
HF_kpu_NH4 = 0.003*1.08**(temp-20)

#denitrification
kdn_an = 0.1*1.08**(temp-20)*(VF_DO/(VF_kd+VF_DO)) #anerobic (.5-3)
kdn_a = 0.035*1.1**(temp-20)*(HF_DO/(HF_kd+HF_DO)) #aerobic (1-4)  (0.9-1.1)

#plant uptake of nitrate
VF_kpu_NO3 = 0.03*.93**(temp-20)    #(0.001-0.9)
HF_kpu_NO3 = 0.4*0.95**(temp-20)     #(0.1-2)

#nitrogen mass balance solutions 
def VF_OrgN():
    
    VF_OrgN1 =(Q*OrgN_i)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    VF_OrgN2 =(Q*VF_OrgN1)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    VF_OrgN =(Q*VF_OrgN2)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    return VF_OrgN
df_VF_OrgN= pd.DataFrame(VF_OrgN())



def HF_OrgN():
    
    HF_OrgN1 =(Qi*VF_OrgN())/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    HF_OrgN2 =(Qi*HF_OrgN1)/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    HF_OrgN =(Qi*HF_OrgN2)/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    return HF_OrgN
df_HF_OrgN= pd.DataFrame(HF_OrgN())

def VF_NH4():
    
    VF_NH41 =(Qi*NH4_i+(km_a*VF_OrgN()*VF_volume/n))/(Q+kn_a*VF_volume/n+(VF_kpu_NH4*VF_volume/n))
    VF_NH42 =(Qi*VF_NH41+(km_a*VF_OrgN()*VF_volume/n))/(Q+kn_a*VF_volume/n+(VF_kpu_NH4*VF_volume/n))
    VF_NH4 =(Qi*VF_NH42+(km_a*VF_OrgN()*VF_volume/n))/(Q+(kn_a*VF_volume/n)+(VF_kpu_NH4*VF_volume/n))
    return VF_NH4

df_VF_NH4= pd.DataFrame(VF_NH4(), columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\VF_Control_NH4.xlsx',df_VF_NH4,[0,600],200,500)

def HF_NH4():
   
    HF_NH41 =(Qi*VF_NH4()+(km_an*HF_OrgN()*HF_volume/n))/(Qo+kn_an*HF_volume/n+(HF_kpu_NH4*HF_volume/n))
    HF_NH42 =(Qi*HF_NH41+(km_an*HF_OrgN()*HF_volume/n))/(Qo+kn_an*HF_volume/n+(HF_kpu_NH4*HF_volume/n))
    HF_NH4 =(Qi*HF_NH42+(km_an*HF_OrgN()*HF_volume/n))/(Qo+kn_an*HF_volume/n+(HF_kpu_NH4*HF_volume/n))
    return HF_NH4

df_HF_NH4= pd.DataFrame(HF_NH4(), columns=['Simulated_'])
plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\HF_Control_NH4.xlsx',df_HF_NH4,[0,600],200,550)



def VF_NO3():
   
    VF_NO31 = ((Q*NO3_i)+(kdn_a*VF_NH4()*VF_volume/n))/(Q+VF_kpu_NO3*VF_volume/n)
    VF_NO32 = ((Q*VF_NO31)+(kdn_a*VF_NH4()*VF_volume/n))/(Q+VF_kpu_NO3*VF_volume/n)
    VF_NO3 = ((Q*VF_NO32)+(kdn_a*VF_NH4()*VF_volume/n))/(Q+VF_kpu_NO3*VF_volume/n)
    return VF_NO3
df_VF_NO3= pd.DataFrame(VF_NO3(), columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\VF_Control_NO3.xlsx',df_VF_NO3,[-10,300],200,250)




def HF_NO3():
   
    HF_NO31 = ((Q*(VF_NO3()))+(kdn_an*HF_NH4()*HF_volume/n))/(Q+HF_kpu_NO3*HF_volume/n)
    HF_NO32 = ((Q*(HF_NO31))+(kdn_an*HF_NH4()*HF_volume/n))/(Q+HF_kpu_NO3*HF_volume/n)
    HF_NO3 = ((Q*(HF_NO32))+(kdn_an*HF_NH4()*HF_volume/n))/(Q+HF_kpu_NO3*HF_volume/n)
    return HF_NO3
    
df_HF_NO3= pd.DataFrame(HF_NO3(), columns=['Simulated_'])
# 
plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\HF_Control_NO3.xlsx',df_HF_NO3,[-10,150],200,125)




# =============================================================================
# path= 'Hourly_Output_Control.xlsx'
# writer= ExcelWriter(path)
# df_VF.to_excel(writer, 'VF')
# df_HF.to_excel(writer, 'HF')
# df_ET.to_excel(writer, 'ET')
# df_VF_DO.to_excel(writer, 'VF_DO')
# df_HF_DO.to_excel(writer, 'HF_DO')
# df_VF_COD.to_excel(writer, 'VF_COD')
# df_HF_COD.to_excel(writer, 'HF_COD')
# df_VF_OrgN.to_excel(writer, 'VF_OrgN')
# df_HF_OrgN.to_excel(writer, 'HF_OrgN')
# df_VF_NH4.to_excel(writer, 'VF_NH4')
# df_HF_NH4.to_excel(writer, 'HF_NH4')
# df_VF_NO3.to_excel(writer, 'VF_NO3')
# df_HF_NO3.to_excel(writer, 'HF_NO3')
# 
# 
# 
# writer.save()
# =============================================================================


# #######Adsorbent Amended CWs###########
# ###### Amended COD ######
#Stover-Kincannon Model
Q = VF_Qi*1000 #L
Qi = Q
Qo = HF_Qo*1000 #L
n=3
VF_k=0.1
VF_kd=VF_k*1.01**(temp-20)
HF_k=0.01
HF_kd=HF_k*1.01**(temp-20)
#Stover-Kincannon Parameters
#VF
A_VF_mu_max= 990*1.01**(temp-20)/24*(VF_DO/(VF_kd+VF_DO)) #mg/L-hr 
A_VF_kB= 868    #mg/L-hr 
rho_zeolite = 877000 #g/m3
r_zeolite = .00025 #m
m_zeolite = 23000 #g
a_zeolite = (3/r_zeolite)*(m_zeolite/rho_zeolite/VF_volume) #m2/m3
VF_qcod= 0.29 #mg COD/g zeolite   (0.1-1)
Ds_zeolite = (4.77*10**-12)*864000/24 #m2/hr   (4-6)
VF_Jcod = -rho_zeolite*VF_qcod*Ds_zeolite 

A_VF_COD1= COD_i-A_VF_mu_max*COD_i/(A_VF_kB+Qi*COD_i/VF_volume/n)+(VF_Jcod*a_zeolite*VF_volume/n)/Q
A_VF_COD2= A_VF_COD1-A_VF_mu_max*A_VF_COD1/(A_VF_kB+Qi*A_VF_COD1/VF_volume/n)+(VF_Jcod*a_zeolite*VF_volume/n)/Q
A_VF_COD= A_VF_COD2-A_VF_mu_max*A_VF_COD2/(A_VF_kB+Qi*A_VF_COD2/VF_volume/n)+(VF_Jcod*a_zeolite*VF_volume/n)/Q
A_VF_COD= np.asarray(A_VF_COD)

df_A_VF_COD= pd.DataFrame(A_VF_COD, columns=['Simulated_'])


plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\VF_Amend_COD.xlsx',df_A_VF_COD,[0,600],200,100)


#HF

A_HF_mu_max= 1609*1.01**(temp-20)/24*(HF_DO/(HF_kd+HF_DO)) #mg/L-hr (4000-8000)
A_HF_kB= 1600   #mg/L-hr (1000-2000)
rho_biochar = 1340000 #g/m3
r_biochar = .0015 #m
m_biochar = 2600 #g
a_biochar = (3/r_biochar)*(m_biochar/rho_biochar/HF_volume) #m2/m3
HF_qcod= 12 #mg COD/g biochar  (12-35)
Ds_biochar = (3.37*10**-11)*864000/24 #m2/hr (4-8)
#t= np.asarray(list(range(1,4105)))
HF_Jcod = rho_biochar*HF_qcod*Ds_biochar

A_HF_COD1= A_VF_COD-A_HF_mu_max*A_VF_COD/(A_HF_kB+Qi*A_VF_COD/HF_volume/n)-(HF_Jcod*a_biochar*HF_volume/n)/Q
A_HF_COD2= A_HF_COD1-A_HF_mu_max*A_HF_COD1/(A_HF_kB+Qi*A_HF_COD1/HF_volume/n)-(HF_Jcod*a_biochar*HF_volume/n)/Q
A_HF_COD= A_HF_COD2-A_HF_mu_max*A_HF_COD2/(A_HF_kB+Qi*A_HF_COD2/HF_volume/n)-(HF_Jcod*a_biochar*HF_volume/n)/Q

A_HF_COD= np.asarray(A_HF_COD)
df_A_HF_COD= pd.DataFrame(A_HF_COD, columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\HF_Amend_COD.xlsx',df_A_HF_COD,[0,600],200,100)


###### Amended nitrogen functions ######
####Rate constants (per hour)
OrgN_0 = 5
NH4_0 = 0     
NO3_0 = 0     
n=3
          
######Rate constants (per day)
VF_k=0.1
VF_kd=VF_k*1.01**(temp-20)
HF_k=0.01
HF_kd=HF_k*1.01**(temp-20)
#plant decomposition
VF_kpd = 0.005*1.04**(temp-20)   #(15-25)
HF_kpd = 0.008*1.04**(temp-20)    #(5-18)

#mineralization
km_a = 0.6*1.08**(temp-20) #aerobic   
km_an = 0.12*1.08**(temp-20) #anaerobic   (0.01,0.09)


#nitrification
kn_a =  0.09*1.08**(temp-20)*(VF_DO/(VF_kd+VF_DO)) #aerobic    (0.5-3)
#vf_kn_an = 0.0000537*1.08**(temp-20) #anaerobic

kn_an =  0.009*1.08**(temp-20)*(HF_DO/(HF_kd+HF_DO)) #aerobic  (0.01,0.15)
#hf_kn_an = 0.01*1.2**(temp-20) #anaerobic

#plant uptake of ammonia 
VF_kpu_NH4 = 0.002*1.08**(temp-20)
HF_kpu_NH4 = 0.025*1.08**(temp-20)

#denitrification
kdn_an = 0.1*1.08**(temp-20) #anerobic (.5-3)
kdn_a = 0.035*1.1**(temp-20) #aerobic (1-4)  (0.9-1.1)
#mass flux parameters
rho_zeolite = 877000 #g/m3
r_zeolite = .00025 #m
m_zeolite = 23000 #g
a_zeolite = (3/r_zeolite)*(m_zeolite/rho_zeolite/VF_volume) #m2/m3
VF_qNH4= 2 #mg NH4/g zeolite   (1-6)

Ds_zeolite = (2.99*10**-12)*864000/24 #m2/day   (2-6)
#mass flux equation
VF_JNH4 = -rho_zeolite*VF_qNH4*Ds_zeolite 

rho_biochar = 1340000 #g/m3
r_biochar = .0015 #m
m_biochar = 2600 #g
a_biochar = (3/r_biochar)*(m_biochar/rho_biochar/HF_volume) #m2/m3
HF_qNH4= 0.05 #mg/g     (0,0.1)
Ds_biochar = (5.6*10**-11)*864000/24 #m2/hr   (1-11)

#mass flux equation

HF_JNH4 = -rho_biochar*HF_qNH4*Ds_biochar

#nitrogen mass balance solutions 
def VF_OrgN():
    
    VF_OrgN1 =(Q*OrgN_i)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    VF_OrgN2 =(Q*VF_OrgN1)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    VF_OrgN =(Q*VF_OrgN2)/(Q-(VF_kpd*VF_volume/n)+(km_a*VF_volume/n))+OrgN_0
    return VF_OrgN
df_VF_OrgN= pd.DataFrame(VF_OrgN())



def HF_OrgN():
    
    HF_OrgN1 =(Qi*VF_OrgN())/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    HF_OrgN2 =(Qi*HF_OrgN1)/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    HF_OrgN =(Qi*HF_OrgN2)/(Qo-(HF_kpd*HF_volume/n)+(km_an*HF_volume/n))+OrgN_0
    return HF_OrgN
df_HF_OrgN= pd.DataFrame(HF_OrgN())

def A_VF_NH4():
    
    A_VF_NH41 =(Q*NH4_i+(km_a*VF_OrgN()*VF_volume/n)+(VF_JNH4*a_zeolite*VF_volume/n))/(Q+(kn_a*VF_volume/n)+(VF_kpu_NH4*VF_volume/n))
    A_VF_NH42 =(Q*A_VF_NH41+(km_a*VF_OrgN()*VF_volume/n)+(VF_JNH4*a_zeolite*VF_volume/n))/(Q+(kn_a*VF_volume/n)+(VF_kpu_NH4*VF_volume/n))
    A_VF_NH4 =(Q*A_VF_NH42+(km_a*VF_OrgN()*VF_volume/n)+(VF_JNH4*a_zeolite*VF_volume/n))/(Q+(kn_a*VF_volume/n)+(VF_kpu_NH4*VF_volume/n))
    return A_VF_NH4
df_A_VF_NH4= pd.DataFrame(A_VF_NH4(), columns=['Simulated_'])

plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\VF_Amend_NH4.xlsx',df_A_VF_NH4,[0,600],200,550)

def A_HF_NH4():
    
    A_HF_NH41 =(Q*A_VF_NH4()+(km_an*HF_OrgN()*HF_volume/n)+(HF_JNH4*a_biochar*HF_volume/n))/(Q+(kn_an*HF_volume/n)+(HF_kpu_NH4*HF_volume/n))
    A_HF_NH42 =(Q*A_HF_NH41+(km_an*HF_OrgN()*HF_volume/n)+(HF_JNH4*a_biochar*HF_volume/n))/(Q+(kn_an*HF_volume/n)+(HF_kpu_NH4*HF_volume/n))
    A_HF_NH4 =(Q*A_HF_NH42+(km_an*HF_OrgN()*HF_volume/n)+(HF_JNH4*a_biochar*HF_volume/n))/(Q+(kn_an*HF_volume/n)+(HF_kpu_NH4*HF_volume/n))
    return A_HF_NH4
df_A_HF_NH4= pd.DataFrame(A_HF_NH4(), columns=['Simulated_'])
plots(r'D:\USF\Research\My Works\Python Scripts\Final Model\Calibration Period\Experimental Effluent\HF_Amend_NH4.xlsx',df_A_HF_NH4,[-20,600],200,550)





# =============================================================================
# path= 'Hourly_Output_Amended.xlsx'
# writer= ExcelWriter(path)
# df_A_HF_COD.to_excel(writer, 'A_HF_COD')
# df_A_VF_COD.to_excel(writer, 'A_VF_COD')
# df_A_VF_NH4.to_excel(writer, 'A_VF_NH4')
# df_A_HF_NH4.to_excel(writer, 'A_HF_NH4')
# #df_A_VF_NO3.to_excel(writer, 'A_VF_NO3')
# #df_A_HF_NO3.to_excel(writer, 'A_HF_NO3')
# 
# writer.save()
# =============================================================================
