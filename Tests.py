# -*- coding: utf-8 -*-

import Gedi as gedi

import numpy as np
import matplotlib.pylab as pl

#####  INITIAL DATA ###########################################################
#np.random.seed(12345)
x = 10 * np.sort(np.random.rand(101))
yerr = 0.2 * np.ones_like(x)
y = np.sin(x) + yerr * np.random.randn(len(x))

###############################################################################
#TESTS FOR THE LIKELIHOOD AND GRADIENT
print 'test 1'
#this sets the kernel
kernel1=gedi.kernel.ExpSquared(11.0,7.0)
#this calculates the kernel's log likelihood
kernel1_test1= gedi.kernel_likelihood.likelihood(kernel1,x,y,yerr)
#this calculates the gradients of the parameters
kernel1_test2= gedi.kernel_likelihood.gradient_likelihood(kernel1,x,y,yerr)
print 'kernel =',kernel1
print 'likelihood =',kernel1_test1
print 'gradients =',kernel1_test2

print 'test 2'
kernel2=gedi.kernel.ExpSineSquared(10.1,1.2,5.1)
kernel2_test1= gedi.kernel_likelihood.likelihood(kernel2,x,y,yerr)
kernel2_test2= gedi.kernel_likelihood.gradient_likelihood(kernel2,x,y,yerr)
print 'kernel =',kernel2
print 'likelihood =',kernel2_test1
print 'gradients =',kernel2_test2

print 'test 3'
kernel3=gedi.kernel.ExpSquared(10.2,7.1)+gedi.kernel.ExpSineSquared(10.1,1.2,5.1)
kernel3_test1= gedi.kernel_likelihood.likelihood(kernel3,x,y,yerr)
kernel3_test2= gedi.kernel_likelihood.gradient_likelihood(kernel3,x,y,yerr)
print 'kernel =',kernel3
print 'likelihood =',kernel3_test1
print 'gradients =',kernel3_test2

print 'test 4'
kernel4=gedi.kernel.ExpSquared(10.2,7.1)*gedi.kernel.ExpSineSquared(10.1,1.2,5.1)
kernel4_test1= gedi.kernel_likelihood.likelihood(kernel4,x,y,yerr)
kernel4_test2= gedi.kernel_likelihood.gradient_likelihood(kernel4,x,y,yerr)
print 'kernel =',kernel4
print 'likelihood =',kernel4_test1
print 'gradients =',kernel4_test2

print '#####################################'

###############################################################################
#TESTS FOR THE OPTIMIZATION
print 'test 5 - optimization'
#this sets the initial kernel
kernel1=gedi.kernel.Exponential(10.0,1.0)+gedi.kernel.WhiteNoise(1.0)
print 'kernel 1 ->', kernel1
#this calculates the initial log likelihood
likelihood1=gedi.kernel_likelihood.likelihood(kernel1,x,y,yerr)
print 'likelihood 1 ->', likelihood1

#this performs the optimization
optimization1=gedi.kernel_optimization.committed_optimization(kernel1,x,y,yerr,max_opt=2)
#it returns optimization[0]=final log likelihood optimization[1]=final kernel
print 'kernel 1 final ->',optimization1[1]
print 'likelihood 1 final ->', optimization1[0]

print '#####################################'

###############################################################################
#TESTS FOR GRAPHICS
print 'test 6 - everything combined'
kernel2=gedi.kernel.ExpSineSquared(10.0,1.0,10.0)+gedi.kernel.Exponential(5.0,1.5)
print 'kernel =',kernel2

xcalc=np.linspace(-1,11,300)  

#computation of the initial mean and standard deviation
[mu,std]=gedi.kernel_likelihood.compute_kernel(kernel1,x,xcalc,y,yerr)
pl.figure()
pl.fill_between(xcalc, mu+std, mu-std, color="k", alpha=0.1)
pl.plot(xcalc, mu+std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu-std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu, color="k", alpha=1, lw=0.5)
pl.errorbar(x, y, yerr=yerr, fmt=".k", capsize=0)
pl.title("Pre-optimization")
pl.xlabel("$x$")
pl.ylabel("$y$")

#run of the optimization algorithms
optimization1=gedi.kernel_optimization.committed_optimization(kernel2,x,y,yerr,max_opt=10)
print 'final kernel = ',optimization1[1]
print 'final likelihood = ', optimization1[0]

#computation of the final mean and standard deviation
[mu,std]=gedi.kernel_likelihood.compute_kernel(optimization1[1],x,xcalc,y,yerr)
pl.figure() 
pl.fill_between(xcalc, mu+std, mu-std, color="k", alpha=0.1)
pl.plot(xcalc, mu+std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu-std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu, color="k", alpha=1, lw=0.5)
pl.errorbar(x, y, yerr=yerr, fmt=".k", capsize=0)
pl.title('Pos-optimization')
pl.xlabel("$x$")
pl.ylabel("$y$")

print '#####################################'

###############################################################################
#TESTS FOR MCMC
print 'test 7 - mcmc'

#definition of the initial kernel, the values you put in here are not important
kernel3=gedi.kernel.ExpSineSquared(10,1,10) + gedi.kernel.WhiteNoise(10.0)
print 'initial kernel =',kernel3
kernel3_test1= gedi.kernel_likelihood.likelihood(kernel3,x,y,yerr)
print 'initia likelihood =',kernel3_test1

#the important is the intervel of the parameters, as it will create the initial
#guess, in this example we believe the amplitude of the ExpSineSquared is 
#somewhere between 5 and 15, the lenght scale between 1 and 4, the period
#between 5 and 10 and the white noise amplitude between 0.1 and 1.
parameters=[[5.0,15.0],[1.0,4.0],[5.0,10.0],[0.1,1]]

#we set the number of runs we want the algorithm to have
runs=50000

#lets run our mcmc
trial=gedi.kernel_mcmc.MCMC(kernel3,x,y,yerr,parameters,runs)

#now lets make graphics of the results
xt=np.linspace(0,runs,runs)
pl.figure()
pl.title('log marginal likelihood')
pl.plot(xt,trial[2],'k-')

f, axarr = pl.subplots(2, 2)
axarr[0, 0].plot(xt, trial[3][0])
axarr[0, 0].set_title('amplitude')
axarr[0, 1].plot(xt, trial[3][1])
axarr[0, 1].set_title('lenght scale')
axarr[1, 0].plot(xt, trial[3][2])
axarr[1, 0].set_title('period')
axarr[1, 1].plot(xt, trial[3][3])
axarr[1, 1].set_title('white noise')
pl.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)

# computation  of the final kernel
xcalc=np.linspace(-1,11,300)  
[mu,std]=gedi.kernel_likelihood.compute_kernel(trial[0],x,xcalc,y,yerr)
pl.figure() #Graphics
pl.fill_between(xcalc, mu+std, mu-std, color="k", alpha=0.1)
pl.plot(xcalc, mu+std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu-std, color="k", alpha=1, lw=0.25)
pl.plot(xcalc, mu, color="k", alpha=1, lw=0.5)
pl.errorbar(x, y, yerr=yerr, fmt=".k", capsize=0)
pl.title('After the mcmc')
pl.xlabel("$time$")
pl.ylabel("$y$")

print 'final kernel =',trial[0]
print 'final likelihood =',trial[1]