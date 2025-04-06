#region imorts
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import PyQt5.QtWidgets as qtw

# importing from previous work on least squares fit
from LeastSquares import LeastSquaresFit_Class
#endregion

#region class definitions
class Pump_Model():
    """
    This is the pump model.  It just stores data.
    """
    def __init__(self): #pump class constructor
        #create some class variables for storing information
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        # place to store data from file
        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        # place to store coefficients for cubic fits
        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        # create two instances (objects) of least squares class
        self.LSFitHead=LeastSquaresFit_Class()
        self.LSFitEff=LeastSquaresFit_Class()

class Pump_Controller():
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()
    
    #region functions to modify data of the model
    def ImportFromFile(self, data):
        """
        This processes the list of strings in data to build the pump model
        :param data: 
        :return: 
        """
        self.Model.PumpName = data[0].strip() #JES Missing Code  #  done
        #data[1] is the units line
        L = data[2].split()
        self.Model.FlowUnits = L[0]  #JES Missing Code  #  Done
        self.Model.HeadUnits = L[1]  #JES Missing Code  #  Done

        # extracts flow, head and efficiency data and calculates coefficients
        self.SetData(data[3:])
        self.updateView()
    
    def SetData(self,data):
        '''
        Expects three columns of data in an array of strings with space delimiter
        Parse line and build arrays.
        :param data:
        :return:
        '''
        #erase existing data
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        #parse new data
        for L in data:
            Cells= L.split()  #JES Missing Code #parse the line into an array of strings  #  Done
            self.Model.FlowData=np.append(self.Model.FlowData, float(Cells[0])) #remove any spaces and convert string to a float  #  Done
            self.Model.HeadData=np.append(self.Model.HeadData, float(Cells[1])) #remove any spaces and convert string to a float  #  Done
            self.Model.EffData=np.append(self.Model.EffData, float(Cells[2])) #remove any spaces and convert string to a float  #  Done

        #call least square fit for head and efficiency
        self.LSFit()
        
    def LSFit(self):
        '''Fit cubic polynomial using Least Squares'''
        self.Model.LSFitHead.x=self.Model.FlowData
        self.Model.LSFitHead.y=self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(3) #calls LeastSquares function of LSFitHead object

        self.Model.LSFitEff.x=self.Model.FlowData
        self.Model.LSFitEff.y=self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3) #calls LeastSquares function of LSFitEff object
    #endregion

    #region functions interacting with view
    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)
    #endregion
class Pump_View():
    def __init__(self):
        """
        In this constructor, I create some QWidgets as placeholders until they get defined later.
        """
        self.LE_PumpName=qtw.QLineEdit()
        self.LE_FlowUnits=qtw.QLineEdit()
        self.LE_HeadUnits=qtw.QLineEdit()
        self.LE_HeadCoefs=qtw.QLineEdit()
        self.LE_EffCoefs=qtw.QLineEdit()
        self.ax=None
        self.canvas=None

    def updateView(self, Model):
        """
        Put model parameters in the widgets.
        :param Model:
        :return:
        """
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """
        Create the plot.
        :param Model:
        :return:
        """
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(3, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        axes = self.ax
        #JES Missing code (many lines to make the graph)
        axes.clear()

        axes.set_xlabel("Flow Rate (gpm)")
        axes.set_xlim(13, 43)
        axes.set_xticks([15, 20, 25, 30, 35, 40])
        axes.tick_params(axis='x', direction='in')

        axes.set_ylabel("Head (ft)")
        axes.set_ylim(5, 75)
        axes.set_yticks([10, 20, 30, 40, 50, 60, 70])
        axes.tick_params(axis='y', direction='in')

        head_data, = axes.plot(Model.FlowData, Model.HeadData, 'ko', markersize=8, markerfacecolor='none', label='Head')
        head_fit, = axes.plot(headx, heady, 'k--', linewidth=2, label='Head (R\u00b2={:.3f})'.format(headRSq)) # might need to put in 1.000

        ax2 = axes.twinx()
        ax2.set_ylabel("Efficiency (%)", color='k')
        ax2.set_ylim(5, 60)
        ax2.set_yticks([10, 20, 30, 40, 50])
        ax2.tick_params(axis='y', direction='in')

        eff_data, = ax2.plot(Model.FlowData, Model.EffData, 'k^', markersize=8, markerfacecolor='none', label='Efficiency')
        eff_fit, = ax2.plot(effx, effy, 'k:', linewidth=2, label='Efficiency (R\u00b2={:.3f})'.format(effRSq)) # might need to put in 0.989

        #axes.set_title("Pump Curve Analysis")  # Remove "#" if necessary

        leg1 = axes.legend(handles=[head_data, head_fit], loc='center left', bbox_to_anchor=(0.0, 0.5))
        leg2 = axes.legend(handles=[eff_data, eff_fit], loc = 'upper right')

        axes.add_artist(leg1)

        self.canvas.draw()

    def setViewWidgets(self, w):
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
#endregion

