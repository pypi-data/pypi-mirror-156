'''
mdbase.const
------------
Global constants for package mdbase.

* The global constants are saved in the form of objects.
* Reason: Parameters can be [re]defined during initialization.
'''

class ExcelParameters:
    '''
    ExcelParameters = object describing format of Excel database files.
    
    Parameters
    ----------
    
    skiprows : int
        numer of initial rows to skip 
    '''
    
    def __init__(self, skiprows=9):
        # Docstring for __init__ are given above in class description.
        # Reason: In this way, the parameters are visible in Spyder/Ctrl+I.
        
        # Initialize parameters
        self.skiprows = skiprows
        
class PlotParameters:
    '''
    PlotParameters = object defining local+global parameters for plotting.
    
    Parameters
    ----------
    
    xlabel, ylabel : str, str
        Labels for X and Y axis.

    logscale : bool; optional, the default is False
        If logscale==True, both X and Y axes are in logarithmic scale.

    e_to_percent : bool; optional, the default is True
        Relevant only to tensile experiments.
        If true, the values of elongation are multiplied by 100,
        i.e. they are converted from epsilon[] to epsilon[%].
        
    rcParams : dict; optional, the default is empty dictionary {}
        The dictionary shoud be formatted for mathplotlib.pyplot.rcParams.
        The argmument is passed to matplotlib.pyplot.
        The initialization procedure creates some default rcParams.
        This argument can override this pre-defined parameters,
        i.e. the default is created anyway
        and then (possibly) supplemented by rcParams argument.
    '''
    
    def __init__(self, xlabel, ylabel,
                 logscale=False, e_to_percent=True, rcParams={}):
        # Docstring for __init__ are given above in class description.
        # Reason: In this way, the parameters are visible in Spyder/Ctrl+I.
        
        # Initialize basic parameters
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.logscale = logscale
        self.e_to_percent = e_to_percent
        self.rcParams = rcParams
        # Set global plot settings using rcParams
        plt.rcParams.update({
            'figure.figsize'     : (8/2.54,6/2.54),
            'figure.dpi'         : 500,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':'})
        # Adjust global plot settings if argument rcParams was defined
        plt.rcParams.update(self.rcParams)
