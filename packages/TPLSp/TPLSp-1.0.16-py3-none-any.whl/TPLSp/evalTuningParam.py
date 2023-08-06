from doctest import DONT_ACCEPT_TRUE_FOR_1
from email.utils import decode_rfc2231
import numpy as np
from scipy.stats import rankdata, spearmanr, pearsonr
import matplotlib.pyplot as plt
from . import TPLSinputchecker

class evalTuningParam:
    
    def __init__(self, cvmdl, perftype, X, Y, compvec, threshvec, subfold = None): 
        """ Evaluating cross-validation performance of a TPLS_cv model at compvec and threshvec
            cvmdl       A TPLS_cv object
            perftype    CV performance metric type. One of LLbinary, negMSE, Pearson, Spearman, AUC, ACC.
            X           The same X as used in TPLS_cv.
            Y           The same Y as used in TPLS_cv.
            compvec     Vector of number of components to test in cross-validation.
            threshvec   Vector of threshold level [0 1] to test in cross-validation.
            subfold     (Optional) vector of subdivision within testing fold to calculate performance. For example scan run division within subject.
        """

        # input checking
        assert(np.isin(perftype,['LLbinary','negMSE','Pearson','Spearman','AUC','ACC'])), 'Unknown performance metric'; self.type = perftype;
        TPLSinputchecker.TPLSinputchecker(X,'X','mat',None,None,1); n, v = X.shape
        Y = TPLSinputchecker.TPLSinputchecker(Y,'Y','colvec',None,None,1)
        compvec = TPLSinputchecker.TPLSinputchecker(compvec,'compvec','rowvec',cvmdl.NComp,1,0,1); compvec = np.sort(compvec); self.compval = compvec;
        threshvec = TPLSinputchecker.TPLSinputchecker(threshvec,'threshvec','rowvec',1,0); threshvec = np.sort(threshvec); self.threshval = threshvec;
        if subfold is None:
            subfold = np.ones((n,1))
        else:
            subfold = TPLSinputchecker.TPLSinputchecker(subfold,'subfold','colvec')
        
        # Perform CV prediction and performance measurement
        perfmat = np.empty((len(compvec),len(threshvec),cvmdl.numfold)); perfmat.fill(np.nan)
        for i in range(cvmdl.numfold):
            print('Fold #'+str(i+1))
            testCVfold = cvmdl.CVfold[:,i] == 1
            Ytest = Y[testCVfold]
            testsubfold = subfold[testCVfold]
            uniqtestsubfold = np.unique(testsubfold)
            for j in range(len(threshvec)):
                predmat = cvmdl.cvMdls[i].predict(compvec,threshvec[j].item(),X[testCVfold.flatten(),:])
                smallperfmat = np.empty((len(compvec),len(uniqtestsubfold)))
                for k in range(len(uniqtestsubfold)):
                    subfoldsel = testsubfold == uniqtestsubfold[k]
                    smallperfmat[:,k] = self.util_perfmetric(predmat[subfoldsel.flatten(),:],Ytest[subfoldsel],perftype)
                perfmat[:,j,i] = np.nanmean(smallperfmat, axis=1)
        
        # prepare output object
        self.perfmat = perfmat; avgperfmat = np.nanmean(perfmat, axis=2) # mean performance
        self.perf_best = np.nanmax(avgperfmat).item() # best mean performance
        row_best,col_best = np.where(avgperfmat==self.perf_best) # coordinates of best point
        self.compval_best = compvec[row_best[0]].item(); self.threshval_best = threshvec[col_best[0]].item(); # component and threshold of best point
        standardError = np.nanstd(perfmat[row_best[0],col_best[0]])/np.sqrt(perfmat.shape[2]); # standard error of best point
        candidates = avgperfmat[:,np.arange(col_best[0]+1)] > (self.perf_best-standardError)
        col_1se,row_1se = np.where(candidates.T) # coordinates of 1SE point
        self.perf_1se = avgperfmat[row_1se[0],col_1se[0]].item(); # performance of 1SE point
        self.compval_1se = compvec[row_1se[0]].item(); self.threshval_1se = threshvec[col_1se[0]].item()
        maxroute = np.max(avgperfmat,0); maxrouteind = np.argmax(avgperfmat,0)
        self.best_at_threshold = np.vstack((maxroute,threshvec,compvec[maxrouteind])).T

    def plot(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        meansurf = np.nanmean(self.perfmat, axis = 2)
        X, Y = np.meshgrid(self.threshval, self.compval)
        ax.plot_surface(X, Y, meansurf, rstride=1, cstride=1,cmap='viridis', edgecolor='none')
        ax.set_xlabel('Proportion of Voxels Left')
        ax.set_ylabel('Number of PLS components')
        ax.set_zlabel(self.type)
        ax.scatter(self.threshval_best,self.compval_best,self.perf_best,c='blue')
        ax.scatter(self.threshval_1se,self.compval_1se,self.perf_1se,c='red')
        ax.scatter(self.threshval,self.best_at_threshold[:,2],self.best_at_threshold[:,0],c='orange')
        plt.show()

    @staticmethod
    def util_perfmetric(predmat,testY,perftype):
        print(predmat.shape)
        print(testY.shape)
        if perftype == 'LLbinary':
            assert(np.all(np.logical_or(testY == 0, testY==1))), 'LL binary can be only calculated for binary measures'
            predmat[testY!=1,:] = 1 - predmat[testY!=1,:] # flip probability
            predmat[predmat>1] = 1; predmat[predmat<=0] = np.finfo(float).tiny # take care of probability predictions outside of range
            Perf = np.nanmean(np.log(predmat),0)
        elif perftype == 'negMSE':
            Perf = -np.nanmean((predmat-testY)**2,0)
        elif perftype == 'ACC':
            assert(np.all(np.logical_or(testY == 0, testY==1))), 'Accuracy can be only calculated for binary measures'
            Perf = np.nanmean(1*(testY==1 & (predmat>0.5)),0)
        elif perftype == 'AUC':
            assert(np.all(np.logical_or(testY == 0, testY==1))), 'AUC can be only calculated for binary measures'
            n = len(testY); num_pos = sum(testY==1); num_neg = n - num_pos
            Perf = 0.5 * np.ones(predmat.shape[1])
            if (num_pos > 0 & num_pos < n):
                ranks = rankdata(predmat,axis=0); Perf = ( sum( ranks[testY==1,:] ) - num_pos * (num_pos+1)/2) / ( num_pos * num_neg)
        elif perftype == 'Pearson':
            Perf = np.zeros(predmat.shape[1])
            for i in range(predmat.shape[1]):
                Perf[i] = pearsonr(testY,predmat[:,i])[0]
        elif perftype == 'Spearman':
            Perf = np.zeros(predmat.shape[1])
            for i in range(predmat.shape[1]):
                Perf[i] = spearmanr(testY,predmat[:,i])[0]
        return Perf