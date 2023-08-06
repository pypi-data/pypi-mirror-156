import numpy as np
from scipy.stats import rankdata
import warnings
from . import TPLSinputchecker

class TPLS:
    
    def __init__(self, X, Y, NComp = 25, W = None, nmc = 0): 
        """ Constructor method for fitting a T-PLS model with given data X and Y.
            X       Numerical numpy matrix of predictors. Typically single-trial betas where each column is a voxel and row is observation
            Y       Numerical numpy column vector to predict. Binary 0 and 1 in case of classification, continuous variable in case of regression
            NComp   (Optional) Number of PLS components to compute. Default is 25.
            W       (Optional) Observation weights. By default, all observations have equal weight.
            nmc     (Optional) 'no mean centering'. Default is 0. If 1, T-PLS will skip mean-centering.
                    This option is only provided in case you already mean-centered the data and want to save some memory usage.
        """

        # input checking
        TPLSinputchecker(X,'X','mat',None,None,1); n, v = X.shape
        Y = TPLSinputchecker(Y,'Y','colvec',None,None,1)
        TPLSinputchecker(NComp,'NComp','scalar',None,1,0,1)
        if W is None: W = np.ones((n,1))
        W = TPLSinputchecker(W,'W','colvec',None,0); W = W/sum(W); # normalize weight sum to 1
        TPLSinputchecker(nmc,'nmc','scalar')
        assert(n==Y.size and n==W.size),'X, Y, and W should have equal number of rows'
        
        # Mean-center variables as needed by SIMPLS algorithm
        self.NComp = NComp; self.MX = W.T @ X; self.MY = W.T @ Y # calculating weighted means of X and Y
        if nmc == 0: # do mean centering
            X = X-self.MX; Y = Y-self.MY # subtract means
        elif np.any(np.abs(self.MX) > 1e-04):
            warnings.warn('Skipped mean centering, but X does not seem to be mean-centered. Results may be invalid')
        
        # allocate memories
        self.pctVar = np.zeros((NComp,1)); self.scoreCorr = np.zeros((NComp,1)); # percent of variance of Y each component explains, weighted correlation between Y and current component
        self.betamap = np.zeros((v,NComp)); self.threshmap = 0.5 * np.ones((v,NComp)); self.zmap = np.zeros((v,NComp)) # output variables
        B = np.zeros((NComp,1)); P2 = np.zeros((n,NComp)); C = np.zeros((v,NComp)); sumC2 = np.zeros((v,1)); r = Y; V = np.zeros((v,NComp)) # interim variables
        WT = W.T; WTY2 = WT @ (Y*Y); W2 = W*W # often-used variables in calculation

        # Perform Arthur-modified SIMPLS algorithm
        Cov = (((W*Y).T)@X).T; normCov = np.linalg.norm(Cov) # initial weighted covariance between X and Y
        for i in range(NComp): # starting loop
            print('Calculating Comp #'+str(i+1))
            P = X@Cov; norm_P = np.sqrt(WT@(P*P)); # this is the component and its weighted stdev
            P = P / norm_P; B[i] = (normCov**2) / norm_P; C[:,i] = Cov.flatten()/norm_P # normalize component, beta, and back-projection coefficient
            self.pctVar[i] = (B[i]*B[i])/WTY2; self.scoreCorr[i] = np.sqrt(self.pctVar[i])

            # Update the orthonormal basis with modified Gram Schmidt
            vi = ((W*P).T @ X).T # weighted covariance between X and current component
            if i != 0: vi = vi - V[:,:i] @ (V[:,:i].T @ vi) # orthogonalize with regards to previous components
            vi = vi/ np.linalg.norm(vi); V[:,i] = vi.flatten() # add the normalized vi to orthonormal basis matrix
            Cov = Cov - vi @ (vi.T @ Cov); Cov = Cov - V[:,:(i+1)] @ (V[:,:(i+1)].T @ Cov); normCov = np.linalg.norm(Cov) # Deflate Covariance using the orthonormal basis matrix

            # Back-projection
            self.betamap[:,i] = (C[:,:(i+1)] @ B[:(i+1)]).flatten() # back-projection of coefficients
            sumC2 = sumC2 + (C[:,i]**2).reshape(v,1); P2[:,i] = (P**2).flatten(); r = r - P*B[i] # some variables that will facilitate computation later
            if i != 0: # no need to calculate threshold for first component
                se = np.sqrt( P2[:,:(i+1)].T @ (W2*(r**2)) ) # Huber-White Sandwich estimator (assume no small T bias)
                self.zmap[:,i] = ( (C[:,:(i+1)] @ (B[:(i+1)]/se))/np.sqrt(sumC2) ).flatten() # back-projected z-statistics
                self.threshmap[:,i] = (v-rankdata(np.abs(self.zmap[:,i])))/v # convert into thresholds between 0 and 1
        
            # check if there's enough covariance to milk
            if normCov < 10*np.finfo(float).eps:
                print('All Covariance between X and Y has been explained. Stopping...'); break
            elif self.pctVar[i] < 10*np.finfo(float).eps: # Proportion of Y variance explained is small
                print('New PLS component does not explain more covariance. Stopping...'); break

    def makePredictor(self,compval,threshval):
        """ Method for extracting the T-PLS predictor at a given compval and threshval
            input   compval     Vector of number of components to use in final predictor
                                (e.g., [3,5] will give you two betamaps, one with 3 components and one with 5 components
                    threshval   Scalar thresholding value to use in final predictor.
                                (e.g., 0.1 will yield betamap where only 10% of coefficients will be non-zero)
            return  betamap     T-PLS predictor coefficient
                    bias        Intercept for T-PLS model.
        """
        compval = TPLSinputchecker(compval,'compval','colvec',self.NComp,1,0,1)
        TPLSinputchecker(threshval,'threshval','scalar',1,0)
        if threshval == 0:
            betamap = self.betamap[:,compval-1] * 0
        else:
            betamap = self.betamap[:,compval-1] * (self.threshmap[:,compval-1] <= threshval)
        bias = self.MY - self.MX @ betamap # post-fitting of bias
        return betamap, bias
    
    def predict(self,compval,threshval,testX):
        """ Method for making predictions on a testing dataset testX
            input   compval     Vector of number of components to use in final predictor
                    threshval   Single number of thresholding value to use in final predictor.
                    testX       Data to be predicted. In same orientation as X
            return  score       Prediction scores on a testing dataset
        """
        TPLSinputchecker(testX,'testX')
        threshbetamap,bias = self.makePredictor(compval,threshval)
        score = bias + testX @ threshbetamap
        return score