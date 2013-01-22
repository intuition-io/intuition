# From: http://statsadventure.blogspot.fr/2012/07/expected-shortfall-portfolio.html
require(MASS)
require(nloptr)

#Covariance structure for the simulation
#give everything a std=.1
n = 4
corr = c(1, .7,  .5,  .1,
              .7,  1,  .4, -.1,
              .5, .4,   1,  .6,
              .1, -.1, .6,  1)

corr = matrix(corr,n,n)

std = matrix(0,n,n)
for(i in 1:n){      
       std[i,i] = .1
}

cov = std %*% corr %*% std

#Simulate 10,000 draws
sim = mvrnorm(n=10000,rep(0,n),cov)

#feasible starting values of equal weights
w = rep(1/n,n)

#ES function.  Mean of values above alpha
es = function(w,sim=NA,alpha=.05){
       ret = sort(sim %*% w)
      
       n = length(ret)
       i = alpha * n
      
       es = mean(ret[1:i])
      
       return(-es)  
}


#linear equality constraint
#note: nloptr requires all functions to have the same signature
eval_g0 <- function(w,sim=NA,alpha=NA) {
       return( sum(w) - 1 )
}

#numerical approximation of the gradient
des = function(w,sim=NA,alpha=.05){
       n = length(w)
       out = w;
       for (i in 0:n){
              up = w;
              dn = w;
              up[i] = up[i]+.0001
              dn[i] = dn[i]-.0001
              out[i] = (es(up,sim=sim,alpha=alpha) - es(dn,sim=sim,alpha=alpha))/.0002
       }
       return(out)
}

#use nloptr to check out gradient
check.derivatives(w,es,des,sim=sim, alpha=.05)

#function to optimize -- a list of objective and gradient
toOpt = function(w,sim=NA,alpha=.05){
       list(objective=es(w,sim=sim,alpha=alpha),gradient=des(w,sim=sim,alpha=alpha))    
}

#equality constraint function.  The jacobian is 1 for all variables
eqCon = function(w,sim=NA,alpha=.05){
       list(constraints=eval_g0(w,sim=NA,alpha=.05),jacobian=rep(1,4))     
}

#optimization options
opts <- list( "algorithm" = "NLOPT_LD_SLSQP",
              "xtol_rel" = 1.0e-7,
              "maxeval" = 1000)

#run optimization and print results
nl = nloptr(w,toOpt,
              lb = rep(0,4),
              ub = rep(1,4),
              eval_g_eq=eqCon,
              opts=opts,
              sim=sim,alpha=.05)

print(nl)

s = nl$solution
obj = nl$objective
