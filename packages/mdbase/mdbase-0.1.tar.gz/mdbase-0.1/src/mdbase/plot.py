'''
mdbase.io
-----------
Plotting functions for package mdbase.    
'''

import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats, scipy.optimize
import seaborn as sns
import mdbase.io as mio

class CorrelationPlot:
    
    def __init__(self, df, rcParams={}):
        # (1) BEFORE initializing plot, update plot parameters
        # (1a) General plot style
        plt.style.use('default')
        # (1b) Default parameters
        plt.rcParams.update({
            'figure.figsize'     : (8/2.54,6/2.54),
            'figure.dpi'         : 500,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'lines.markersize'   : 3,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':',
            'legend.handlelength': 1})
        # (1c) Optional modification of default parameters
        if rcParams != {}: plt.rcParams.update({rcParams})
        # (2) AFTER parameters have been updated, initialize the plot  
        # (each CorrelationPlot object contains fig,ax + dataset
        fig,ax = plt.subplots()
        self.fig = fig
        self.ax  = ax
        self.df  = df
        
    def correlation(self, P1, P2, category=None, marker='rx', label=None):
        # Test, if category was given
        # (trick: pandas.Series cannot be compared with scalar => np.any
        if np.any(category) == None:
            ds = self.df
        else:
            ds = self.df[category]
        self.ax.plot(ds[P1], ds[P2], marker, label=label)
    
    def regression(self, P1, P2, category=None, 
            rtype='linear', marker='k-', label=None):
        # Test, if category was given
        # (trick: pandas.Series cannot be compared with scalar => np.any
        if np.any(category) == None:
            ds = self.df
        else:
            ds = self.df[category]
        # Remove NaN values before regression
        # (scipy.optimize.curve_fit does not work with NaN's
        ds = ds[[P1,P2]]
        ds = ds.dropna()
        # Sort values
        ds = ds.sort_values(by=[P1,P2])
        # Get regression type & define regression function
        if rtype == 'linear':
            def linear(X,a,b): return(a*X + b)
            self.regression_func = linear
        elif rtype == 'quadratic':
            def quadratic(X,a,b,c): return(a*X**2 + b*X + c)
            self.regression_func = quadratic 
        elif rtype == 'power':
            def power(X,n,c): return(c*X**n)
            self.regression_func = power
        else:
            print('Unknown regression type (rtype) - no action.')    
        # Calculate regression
        X,Y = (ds[P1],ds[P2])
        par,cov = scipy.optimize.curve_fit(self.regression_func,X,Y)
        # Calculate coefficient of determination
        # R2 values: 1 = perfect, 0 = estimate~average(Y), negative = very bad 
        # https://en.wikipedia.org/wiki/Coefficient_of_determination
        Yave = np.average(Y)
        Yfit = self.regression_func(X,*par)
        SSres = np.sum((Y-Yfit)**2)
        SStot = np.sum((Y-Yave)**2)
        R2 = 1 - SSres/SStot
        # Show regression in graph
        self.ax.plot(X,self.regression_func(X,*par), marker, label=label)
        # Print coefficient of determination to stdout
        reg_func_name = self.regression_func.__name__
        print(f'Regression function: {reg_func_name:s};', end=' ')
        print(f'R2 = {R2:.2f}')
    
    def finalize(self, xlabel, ylabel,
            grid=True, legend=True, legend_loc='lower right'):
        # Obligatory arguments = XY-labels
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        # Addigional default options
        # (can be modified manually using CorrelationPlot.ax object
        self.ax.grid()
        if legend: self.ax.legend(loc=legend_loc)
        self.fig.tight_layout()
        
    def save(self, output_graph='default'):
        if output_graph == 'default': output_graph = sys.argv[0]+'.png'
        self.fig.savefig(output_graph)
        
class ScatterplotMatrixGraph:
    
    def __init__(self, df, properties, font_scale=1.1):
        # Set SNS parameters
        sns.set_style('ticks')
        sns.set(
            style='ticks', context='paper',
            palette='RdBu', font_scale=font_scale)
        # Save dataframe as a property
        self.df = df
        self.properties = properties
        
    def draw(self, correlation_coeff=False, decimals=3):
        ds = self.df[list(self.properties.keys())]
        ds = ds.dropna()
        self.grid = sns.pairplot(
            ds, kind='reg', diag_kind='kde',
            plot_kws=({'truncate':False, 'ci':95}))
        if correlation_coeff == True:
            self._pairplot_correlation_coefficients(decimals=decimals)
    
    def finalize(self, ylabel_shift=0):
        self.grid.fig.set_size_inches(16/2.54,16/2.54)
        self.grid.fig.set_dpi(300)
        self._pairplot_custom_labels()
        self._pairplot_align_ylabels(ylabel_shift)
        self.grid.tight_layout()
        
    def _pairplot_custom_labels(self):
        grid_size = len(self.properties)
        for i in range(grid_size):
            for j in range(grid_size):
                xlabel = self.grid.axes[i][j].get_xlabel()
                ylabel = self.grid.axes[i][j].get_ylabel()
                if xlabel in self.properties.keys():
                    self.grid.axes[i][j].set_xlabel(self.properties[xlabel])
                if ylabel in self.properties.keys():
                    self.grid.axes[i][j].set_ylabel(self.properties[ylabel])
                    
    def _pairplot_align_ylabels(self, ylabel_shift = -0.4):
        for ax in self.grid.axes[:,0]:
            ax.get_yaxis().set_label_coords(ylabel_shift,0.5)
    
    def _pairplot_correlation_coefficients(self, decimals):
        # Scipy + matplotlib: add Pearson's r to upper-right corners
        # Trick #0: for k in dict: for-cycle with dictionary returns keys
        # Trick #1: for i,k in enumerate(dict): trick0+enumerate => index+key
        # Trick #2: ax.text(x,y,s,transform=ax.transAxes) rel.coords ~ (0;1)
        for index1,column1 in enumerate(self.properties.keys()):
            for index2,column2 in enumerate(self.properties.keys()):
                (corr,pval) = scipy.stats.pearsonr(
                    self.df[column1],self.df[column2])
                if column1 != column2:
                    self.grid.axes[index1,index2].text(
                        0.1,0.9, f'$r$ = {corr:.{decimals}f}',
                        transform=self.grid.axes[index1,index2].transAxes)

    
    def save(self, output_graph='default'):
        if output_graph == 'default': output_graph = sys.argv[0]+'.png'
        # plt.tight_layout()
        plt.savefig(output_graph)
        
class CorrelationMatrixTable:
    
    def __init__(self, df, properties, rcParams={}):
        # (1) Initialize basic parameters
        # (data and properties to correlate
        self.df  = df
        self.properties = properties
        # (2) BEFORE initializing plot, update plot parameters
        # (2a) General plot style
        plt.style.use('default')
        # (2b) Default parameters
        plt.rcParams.update({
            'figure.figsize'     : (17/2.54,12/2.54),
            'figure.dpi'         : 500,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'lines.markersize'   : 3,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':',
            'legend.handlelength': 1})
        # (2c) Optional modification of default parameters
        if rcParams != {}: plt.rcParams.update({rcParams})
        # (3) AFTER parameters have been updated, initialize the plots 
        # (each CorrelationMatrixTable contains two plots - r-coeff + p-values
        fig1,ax1 = plt.subplots()
        self.fig1 = fig1
        self.ax1  = ax1
        fig2,ax2 = plt.subplots()
        self.fig2 = fig2
        self.ax2  = ax2
        
    def draw(self, 
             cmap_r='Reds', cmap_p='Blues_r', 
             decimals_r=2, decimals_p=2, cbars=True):
        # (1) Prepare data for calculations
        ds = self.df[list(self.properties.keys())]
        ds = ds.dropna()
        # (2) Prepare empty tables to save results
        n = len(self.properties)
        r_values = np.zeros((n,n))
        p_values = np.zeros((n,n))
        # (3) Calculate correlations
        for (i,column1) in enumerate(self.properties.keys()):
            for (j,column2) in enumerate(self.properties.keys()):
                (corr,pval) = scipy.stats.pearsonr(ds[column1],ds[column2])
                r_values[i,j] = round(corr,5)
                p_values[i,j] = round(pval,5)
        # (4) Prepare for plotting... 
        # (Flip rows so that the main diagonal started in upper left corner
        # (default: [0,0] = start of the main diagonal = lower left corner
        r_values = np.flipud(r_values)
        p_values = np.flipud(p_values)
        # (5a) Draw cmatrix for r-values = sns.heatmap
        # ...draw cmatrix = heatmap
        my_format = "."+str(decimals_r)+"f"
        sns.heatmap(data=r_values, ax=self.ax1,
            annot=True, fmt=my_format, cmap=cmap_r, cbar=cbars,
            linecolor='white', linewidth=2)
        # (5b) Draw cmatrix for p-values = sns.heatmap with custom colormap
        # ...draw cmatrix = heatmap
        my_format = "."+str(decimals_p)+"f"
        sns.heatmap(data=p_values, ax=self.ax2,
            annot=True, fmt=my_format, cmap=cmap_p, cbar=cbars,
            linecolor='white', linewidth=2)
        
    def finalize(self):
        # Prepare labels
        # (labels for y-axis must be reversed - like the rows
        my_xticklabels = self.properties.values()
        my_yticklabels = list(reversed(list(self.properties.values())))
        # Set limits, ticklabels...
        n = len(self.properties)
        for ax in (self.ax1, self.ax2):
            ax.set_ylim(0,n)
            ax.set_xticklabels(my_xticklabels, rotation='vertical')
            ax.set_yticklabels(my_yticklabels, rotation='horizontal')
        # Final adjustments
        for fig in (self.fig1,self.fig2):
            fig.tight_layout()

    def save(self, output_table_r='default', output_table_p='default'):
        if output_table_r == 'default': output_table_r = sys.argv[0]+'_1r.png'
        if output_table_p == 'default': output_table_p = sys.argv[0]+'_2p.png'
        self.fig1.savefig(output_table_r)
        self.fig2.savefig(output_table_p)

class BoxPlot:
    
    def __init__(self, df, rcParams={}):
        # (1) BEFORE initializing plot, update plot parameters
        # (1a) General plot style 
        sns.set_style('whitegrid')
        # (1b) fine-tuning of plot parameters
        plt.rcParams.update({
            'figure.figsize'     : (6/2.54,6/2.54),
            'figure.dpi'         : 300,
            'font.size'          : 8,
            'lines.linewidth'    : 0.6,
            'lines.markersize'   : 4,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':'})
        # (1c) Optional modification of default parameters
        if rcParams != {}: plt.rcParams.update({rcParams})
        # (2) AFTER parameters have been updated, initialize the plot  
        # (each CorrelationPlot object contains fig,ax + dataset
        fig,ax = plt.subplots()
        self.fig = fig
        self.ax  = ax
        self.df  = df

    def add_boxes(self, x, y, categories, colors, width=0.5):
        sns.boxplot(
            data=self.df, x=x, y=y,
            order=categories, palette=colors, width=0.5)
    
    def finalize(self, xlabel, ylabel):
        self.ax.set(xlabel = xlabel, ylabel = ylabel)
        self.fig.tight_layout()
    
    def save(self, output_graph='default'):
        if output_graph == 'default': output_graph = sys.argv[0]+'.png'
        self.fig.savefig(output_graph)

    def statistics(self, X, Y, CATS, output_stats='default'):
        # Name of TXT file with output statistics that corresponds to BoxPlot
        if output_stats == 'default': output_stats = sys.argv[0]+'.txt'
        # Start writing to both standard output and output_stats file
        logfile = mio.Logger(output_stats)
        # Calulate and print statistics
        print('Correlation matrix table (p-values)')
        print('-----------------------------------')
        for category1 in CATS:
            print(f'{category1:8s}', end='')
            for category2 in CATS:
                xdata = self.df[Y][self.df[X] == category1]
                ydata = self.df[Y][self.df[X] == category2]
                t,p = scipy.stats.ttest_ind(xdata, ydata, equal_var = True)
                print(f'{p:8.4f}', end=' ')
            print()
        # Close dual output
        logfile.close()
    