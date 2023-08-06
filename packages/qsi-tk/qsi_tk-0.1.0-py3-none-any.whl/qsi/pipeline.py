from . import io
import os.path
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA, SparsePCA, KernelPCA, TruncatedSVD
from sklearn.manifold import TSNE, MDS
from .vis import *
from .dr import dataset_dct_row_wise
from .dr import mf, lda
from IPython.core.display import HTML, display

def analyze(id, shift = 100):
    '''
    id : dataset id or a full path
    '''
    display(HTML('<h2>数据加载</h2>'))

    if (id in io.DATASET_MAP.keys()):
        X, y, X_names, _ = io.LoadDataSet(id, shift = shift)
    elif os.path.exists(id):
        X, y, X_names, _ = io.OpenDataSet(id, shift = shift)

    display(HTML('<hr/><h2>预处理</h2><h3>滤波</h3>'))

    # Savgol filtering
    np.set_printoptions(precision=2)
    X_sg = savgol_filter(X, window_length = 9, polyorder = 3, axis = 1)  # axis = 0 for vertically; axis = 1 for horizontally
    plt.figure(figsize = (40,10))
    plt.scatter(X_names, np.mean(X_sg,axis=0).tolist()) 
    plt.title(u'Averaged Spectrum After Savitzky-Golay Filtering', fontsize=30)

    display(HTML('<hr/><h3>特征缩放</h3>'))
    # normalization

    scaler = StandardScaler()
    scaler.fit(X)
    X_scaled = scaler.transform(X)

    # scaling to [0,1]

    mm_scaler = MinMaxScaler()
    X_mm_scaled = mm_scaler.fit_transform(X)

    display(HTML('<hr/><h2>降维</h2>'))
    # Dimension Reduction & Visualization

    # SparsePCA(n_components=None, alpha=1, ridge_alpha=0.01, max_iter=1000, tol=1e-08, method=’lars’, n_jobs=1, U_init=None, V_init=None, verbose=False, random_state=None)    # [Warn] SparsePCA takes very long time to run.
    X_spca = SparsePCA(n_components=2).fit_transform(X) # keep the first 2 components. default L1 = 1; default L2 = 0.01 pca.fit(X) X_spca = pca.transform(X) print(X_spca.shape)
    ax = plotComponents2D(X_spca, y)
    ax.set_title('Sparse PCA')
    plt.show()    
    display(HTML('<hr/>'))

    X_kpca = KernelPCA(n_components=2, kernel='rbf').fit_transform(X) # keep the first 2 components. default gamma = 1/n_features
    ax = plotComponents2D(X_kpca, y)
    ax.set_title('Kernel PCA')
    plt.show()
    display(HTML('<hr/>'))

    X_tsvd = TruncatedSVD(n_components=2).fit_transform(X)
    ax = plotComponents2D(X_tsvd, y)
    ax.set_title('Truncated SVD')    
    plt.show()
    print('PCA is (truncated) SVD on centered data (by per-feature mean substraction). If the data is already centered, those two classes will do the same. In practice TruncatedSVD is useful on large sparse datasets which cannot be centered easily. ')
    display(HTML('<hr/>'))   

    X_tsne = TSNE(n_components=2).fit_transform(X)
    ax = plotComponents2D(X_tsne, y)
    ax.set_title('t-SNE')
    plt.show()
    print('t-SNE (t-distributed Stochastic Neighbor Embedding) is highly recommended to use another dimensionality reduction method (e.g. PCA for dense data or TruncatedSVD for sparse data) to reduce the number of dimensions to a reasonable amount (e.g. 50) if the number of features is very high. This will suppress some noise and speed up the computation of pairwise distances between samples.')
    display(HTML('<hr/>'))

    X_mds = MDS(n_components=2).fit_transform(X_scaled)
    ax = plotComponents2D(X_mds, y)
    plt.show()
    print('MDS (Multidimensional scaling) is a simplification of kernel PCA, and can be extensible with alternate kernels. PCA selects influential dimensions by eigenanalysis of the N data points themselves, while MDS (Multidimensional Scaling) selects influential dimensions by eigenanalysis of the N2 data points of a pairwise distance matrix. This has the effect of highlighting the deviations from uniformity in the distribution. Reference manifold.ipynb')
    display(HTML('<hr/>'))

    Z = dataset_dct_row_wise(X, K = 2, verbose = False)
    ax = plotComponents2D(Z, y)
    ax.set_title('DCT')
    plt.show()
    display(HTML('<hr/>'))
    
    for alg in mf.get_algorithms():
        W,_,_,_ = mf.mf(X_mm_scaled, k = 2, alg = alg, display = False) # some MFDR algs (e.g., NMF) require non-negative X
        ax = plotComponents2D(W, y)
        ax.set_title(alg)
        plt.show()
        display(HTML('<hr/>'))
    
    X_lda = lda(X, y)
    ax = plotComponents2D(X_lda, y)
    ax.set_title('LDA')
    plt.show()
    display(HTML('<hr/>'))