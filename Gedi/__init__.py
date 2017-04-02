# -*- coding: utf-8 -*-

##### Necessary scripts to everything work #####
"""
    Kernel: contains all the developed kernels
    
    Kernel_likelihood: contains all the programs for the log likelihood
calculation and more

    Kernel_optimization: contains all the optimization algorithms implemented

    Kernel_mcmc: a random walk metropolis hastings algorithm developed to 
optimize the gaussian processes

    RV_function: contains two functions that simualate radial velocity signals 
"""

import kernel
import kernel_likelihood 
import kernel_optimization
import kernel_mcmc

import RV_function