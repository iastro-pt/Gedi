# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 14:51:50 2017

@author: camacho
"""

import kernel as kl
import kernel_likelihood as lk

import numpy as np
import inspect

##### markov chain monte carlo #####
"""
    MCMC() perform the markov chain monte carlo to find the optimal parameters
of a given kernel.
    The algorithm needs improvements as it is very inefficient.

    Parameters
kernel = kernel in use
x = range of values of the independent variable (usually time)
y = range of values of te dependent variable (the measurments)
yerr = error in the measurments
parameters = the interval of the kernel parameters (check the Tests.py
            understand it better)
runs = the number of times the mcmc runs, 50000 by definition, its a lot but
    this version of the mcmc its still very inefficient, I hope to release a
    better one in the future
        
""" 
def MCMC(kernel,x,y,yerr,parameters,runs=50000):
    #to not loose que original kernel and data
    kernelFIRST=kernel;xFIRST=x
    yFIRST=y;yerrFIRST=yerr

    initial_params= [0]*len(parameters)
    for i in range(len(parameters)):
        initial_params[i]=np.random.uniform(parameters[i][0],parameters[i][1])    
    first_kernel=new_kernel(kernelFIRST,initial_params)        
    first_likelihood=lk.likelihood(first_kernel,x,y,yerr)
    first_calc=lk.gradient_likelihood(first_kernel,x,y,yerr)
    print first_kernel,first_likelihood        
    
    i=0
    #a better way to define the step is needed
    step=5e-3 
    #to save the evolution of the log likelihood
    running_logs=[] 
    #to save the evolution of the parameters
    params_number=len(parameters) 
    params_list = [[] for _ in range(params_number)] 
    
    #lets run the mcmc
    while i<runs:
        u=np.random.uniform(0,1)
        
        #lets make new parameters
        guess_params=[np.abs(n+(step)*np.random.randn()) for n in initial_params]
        
        #limits of the variation of the parameters
        for j in range(len(guess_params)):
            if guess_params[j]<parameters[j][0]:
                guess_params[j]=parameters[j][0]
            if guess_params[j]>parameters[j][1]:
                guess_params[j]=parameters[j][1]

        #lets see if we keep the new parameters or not 
        second_kernel=new_kernel(kernelFIRST,guess_params)        
        second_likelihood=lk.likelihood(second_kernel,x,y,yerr)
#        second_calc=lk.gradient_likelihood(second_kernel,x,y,yerr)        
        
        for j in range(len(guess_params)):
            prior=np.exp(first_likelihood)*initial_params[j]
            posterior=np.exp(second_likelihood)*guess_params[j]
            if prior<1e-300:
                ratio=1
                initial_params[j]=guess_params[j]                
            else:
                ratio = posterior/prior
                if u<np.minimum(1,ratio):
                    initial_params[j]=guess_params[j]
                else:
                    initial_params[j]=initial_params[j]   

            params_list[j].append(initial_params[j])

#A better implementation needs to be found for the commented steps
#        #lets see if we are going the right direction
#        check_sign=[]        
#        for ij in range  (len(second_calc)):
#            check_sign.append(first_calc[ij]*second_calc[ij])
#        check_it=all(check_sign>0 for check_sign in check_sign)
#        if check_it is True:                    
#            step=1.2*step #new bigger step to speed up the convergence            
#        else:
#            step=0.5*step #new smaller step to redo the calculations

        #lets define the new kernel
        first_kernel=new_kernel(kernelFIRST,initial_params)
        first_likelihood=lk.likelihood(first_kernel,x,y,yerr)
#        first_calc=lk.gradient_likelihood(first_kernel,x,y,yerr)
        running_logs.append(first_likelihood)
        i+=1
    
    #final kernel and log likelihood
    final_kernel=new_kernel(kernelFIRST,initial_params)
    final_likelihood=lk.likelihood(final_kernel,x,y,yerr)
    
    return [final_kernel,final_likelihood,running_logs,params_list]


##### auxiliary calculations #####
"""
    new_kernel() updates the parameters of the kernels as the mcmc advances
    
    Parameters
kernelFIRST = original kernel in use
b = new parameters or new hyperparameters if you prefer using that denomination
"""
def new_kernel(kernelFIRST,b): #to update the kernels
    if isinstance(kernelFIRST,kl.ExpSquared):
        return kl.ExpSquared(b[0],b[1])
    elif isinstance(kernelFIRST,kl.ExpSineSquared):
        return kl.ExpSineSquared(b[0],b[1],b[2])
    elif  isinstance(kernelFIRST,kl.RatQuadratic):
        return kl.RatQuadratic(b[0],b[1],b[2])
    elif isinstance(kernelFIRST,kl.Exponential):
        return kl.Exponential(b[0],b[1])
    elif isinstance(kernelFIRST,kl.Matern_32):
        return kl.Matern_32(b[0],b[1])
    elif isinstance(kernelFIRST,kl.Matern_52):
        return kl.Matern_52(b[0],b[1])
    elif isinstance(kernelFIRST,kl.ExpSineGeorge):
        return kl.ExpSineGeorge(b[0],b[1])
    elif isinstance(kernelFIRST,kl.WhiteNoise):
        return kl.WhiteNoise(b[0])
    elif isinstance(kernelFIRST,kl.Sum):
        k1_params=[]
        for i in range(len(kernelFIRST.k1.pars)):
            k1_params.append(b[i])    
        k2_params=[]
        for j in range(len(kernelFIRST.k2.pars)):
            k2_params.append(b[len(kernelFIRST.k1.pars)+j])
        new_k1=new_kernel(kernelFIRST.k1,k1_params)
        new_k2=new_kernel(kernelFIRST.k2,k2_params)
        return new_k1+new_k2
    elif isinstance(kernelFIRST,kl.Product):
        k1_params=[]
        for i in range(len(kernelFIRST.k1.pars)):
            k1_params.append(b[i])    
        k2_params=[]
        for j in range(len(kernelFIRST.k2.pars)):
            k2_params.append(b[len(kernelFIRST.k1.pars)+j])
        new_k1=new_kernel(kernelFIRST.k1,k1_params)
        new_k2=new_kernel(kernelFIRST.k2,k2_params)
        return new_k1*new_k2
    else:
        print 'Something is missing'