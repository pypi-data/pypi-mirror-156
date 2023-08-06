import numpy as np
from . import TPLS
from . import TPLSinputchecker

class TPLS_cv:
    
    def __init__(self, X, Y, CVfold, NComp = 25, W = None, nmc = 0): 
        """ Constructor method for fitting a cross-validation T-PLS model
            X       Numerical matrix of predictors. Typically single-trial betas where each column is a voxel and row is observation
            Y       Variable to predict. Binary 0 and 1 in case of classification, continuous variable in case of regression
            CVfold  Cross-validation testing fold information. Can either be a vector or a matrix, the latter being more general.
                    Vector: n-by-1 vector. Each element is a number ranging from 1 ~ numfold to identify which testing fold eachobservation belongs to
                    Matrix: n-by-numfold matrix. Each column indicates the testing data with 1 and training data as 0.
                    Example: For leave-one-out CV, Vector would be 1:n, Matrix form would be eye(n)
                    Matrix form is more general as it can have same trial be in multiple test folds
            NComp   (Optional) Number of PLS components to compute. Default is 25.
            W       (Optional) Observation weights. Optional input. By default, all observations have equal weight.
                    Can either be a n-by-1 vector or a n-by-nfold matrix where each column is observation weights in that CV fold
            nmc     (Optional) 'no mean centering'. See TPLS for more detail.
        """

        # input checking
        TPLSinputchecker.TPLSinputchecker(X,'X','mat',None,None,1); n = X.shape[0]
        Y = TPLSinputchecker.TPLSinputchecker(Y,'Y','colvec',None,None,1)
        CVfold = np.atleast_2d(CVfold) # could be a vector, could be a matrix
        TPLSinputchecker.TPLSinputchecker(CVfold,'CVfold')
        TPLSinputchecker.TPLSinputchecker(NComp,'NComp','scalar',None,1,0,1)
        if W is None: W = np.ones((n,1))
        W = np.atleast_2d(W) # could be a vector, could be a matrix
        TPLSinputchecker.TPLSinputchecker(W,'W',None,None,0);
        TPLSinputchecker.TPLSinputchecker(nmc,'nmc','scalar')
        assert(n==Y.size and n==CVfold.shape[0] and n==W.shape[0]),'X, Y, W, and CV fold should have same number of rows'
        self.CVfold, self.numfold = self.prepCVfold(CVfold) # convert CVfold into matrix form, if not already
        if W.shape[1] == 1: W = np.repeat(W,self.numfold,1) # convert into matrix form, if not already
        
        self.NComp = NComp
        self.cvMdls = []
        for i in range(self.numfold):
            print('Fold #'+str(i+1))
            train = self.CVfold[:,i] == 0
            self.cvMdls.append(TPLS.TPLS(X[train.flatten(),:],Y[train],NComp,W[train,i],nmc))

    @staticmethod
    def prepCVfold(inCVfold):
        """ prepare CV fold data into a matrix form, which is more generalizable """
        if inCVfold.shape[1] == 1: # vector
            uniqfold = np.unique(inCVfold); nfold = len(uniqfold)
            CVfold = np.zeros((inCVfold.shape[0],nfold))
            for i in range(nfold):
                CVfold[:,i] = 1 * np.atleast_2d(inCVfold == uniqfold[i]).T
        elif inCVfold.shape[1] > 1: # matrix
            nfold = inCVfold.shape[1]; CVfold = inCVfold
            if np.any(CVfold != 0 and CVfold != 1):
                raise Exception('Non-binary element in matrix form CVfold. Perhaps you meant to use vector form?')
        else:
            raise Exception("unexpected size of CVfold")
        return CVfold, nfold