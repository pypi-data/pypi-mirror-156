import datetime

import numpy as np
from scipy import signal as si
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import seaborn as sns

from plotting import multi_yax_plot,update_legend

def dataIsolate(data, aggPeriod, 
                highSTDdict,
                lowSTDdict):
    '''
        function to isolate data peiods for SISO System Identification
        
        Parameters
        ----------
        data : pandas - DataFrame
            Input DataFrame
        
        aggPeriod : int - minutes
            Period over which to aggregate data for std - minutes
            
        highSTDdict : dictionary
            keys:   tags that need to have a high STD
            values: min STD limit allowed for each tag
    
        lowSTDdict : dictionary
            keys:   tags that need to have a low STD 
            values: max STD limit allowed for each tag
    
        Returns
        -------
        s : pandas - DataFrame
        columns - start & end DateTimes sorted decending according to 
        highSTDtags calculated STD's
    '''
    
    tags = list(highSTDdict.keys()) + list(lowSTDdict.keys())
    s = data[tags].resample(str(aggPeriod)+"T", closed="left").std()
    
    s["mask"] = True
    for key in highSTDdict.keys():s["mask"] = s["mask"] & (s[key]>highSTDdict[key])
    for key in lowSTDdict.keys(): s["mask"] = s["mask"] & (s[key]<lowSTDdict [key])
           
    s = s.loc[s["mask"],:]
    s = s.sort_values(by = [list(highSTDdict.keys())[0]], ascending = 0).drop(["mask"],axis=1)
    
    s["startDateTime"] = s.index
    s["endDateTime"]   = s.index + datetime.timedelta(minutes=aggPeriod)
    s = s.reset_index().iloc[:,1:]

    return s

class TransferFunctionFit:
    def __init__(self, num, den, delay):
        self.num   = num   # transfer function numerator:   list
        self.den   = den   # transfer function denominator: list
        self.delay = delay # input-output delay:            int (seconds)
        self.R2    = None
        
    def gen_response(self, u, y0):
        # sampling interval in seconds
        dt = np.median((u.index[1:]-u.index[:-1]).seconds)
        
        # Delay input
        u_shift = np.repeat(u[0], int(round(self.delay/dt))+1)
        u       = np.array((u_shift.tolist() + u.values.tolist())\
                           [:u.shape[0]])-u[0]
            
        # Discrete time intervals            
        t  = np.arange(0,u.shape[0]*dt, dt)
        
        # Generate output   
        return si.TransferFunction(self.num,self.den).output(u,t)[1]+y0
    
    def optimize(self, u, y, iterations=1):
        for _ in range(iterations):
            
            # Set intial parameters and optimization bounds
            #------------------------------------------------------------------
            params_0 = self.num + self.den
            l_bounds = []
            u_bounds = []
            for el in params_0:
                if   el==0:l_bounds.append(-1e-100); u_bounds.append(1e-100 )  
                elif el>0 :l_bounds.append(el*0.01); u_bounds.append(el*1000)
                else      :l_bounds.append(el*1000.);u_bounds.append(el*.01 )
            if round(params_0[-1],1)==1: 
                l_bounds[-1]=1
                u_bounds[-1]=1+1e-15 
            if round(params_0[-2],2)==1 and round(params_0[-1],1)==0:
                l_bounds[-2]=1
                u_bounds[-2]=1+1e-15 
            
            # Fit numerator and denominator
            #------------------------------------------------------------------
            def model(u, *params):
                self.num   = params[:len(self.num)]
                self.den   = params[len(self.num):]
                return self.gen_response(u, y[0])
            params = curve_fit(model, u, y, 
                               p0 = params_0, 
                               bounds=(l_bounds,u_bounds))[0]
            self.num = params[:len(self.num)].tolist()
            self.den = params[len(self.num):].tolist()

            # Calc Delay
            #------------------------------------------------------------------
            if self.delay != 0:
                dt = np.median((u.index[1:]-u.index[:-1]).seconds)
                c_m = {}
                for de in range(0,int(u.shape[0]*0.2*dt),int(dt)):
                    self.delay = de
                    y_m        = self.gen_response(u, y[0])
                    c_m[de]    = np.corrcoef(y_m,y)[0,1]
                self.delay = max(c_m, key=c_m.get)
            
        #----------------------------------------------------------------------
        SSres   =  np.sum((y - self.gen_response(u, y[0]))**2)
        SStot   =  np.sum((y - np.mean(y))**2)
        self.R2 = (1 - SSres/SStot)

def auto_id(data, 
             aggPeriod=30, 
             optimize_iters = 1, 
             inpt="", 
             outp="", 
             highSTDdict={}, 
             lowSTDdict={},
             num=[1], 
             den=[20,0], 
             delay=0,
             minute_shift=datetime.timedelta(minutes=0),
             period_index=range(2),
             y0 = None):

    #--------------------------------------------------------------------------
    s = dataIsolate(data        = data,
                    aggPeriod   = aggPeriod,
                    highSTDdict = highSTDdict,
                    lowSTDdict  = lowSTDdict,
                    ).round(4)  
    
    print (s.shape)
    if period_index is None: period_index = range(5)
    s = s.iloc[period_index,:]
    print (s)
    fig, ax = plt.subplots(s.shape[0],2, sharey=False, figsize=(25,12))
    plt.subplots_adjust(wspace=0.55)
    
    for i,idx in enumerate(s.index):
        mask = (data.index > (s.loc[idx,"startDateTime"]) + minute_shift) &\
               (data.index < (s.loc[idx,"endDateTime"  ]) + minute_shift)
        di = data.loc[mask,list(highSTDdict.keys())+list(lowSTDdict.keys())].fillna(method="pad")
        di = di.loc[~di.isnull().any(axis=1),:]
        
        #----------------------------------------------------------------------
        tff = TransferFunctionFit(num,den,delay)
        tff.optimize(di[inpt],di[outp],optimize_iters)
        y0_ = y0
        if y0 is None: y0_ = di[outp][0]
        y = tff.gen_response(di[inpt], y0_)
    
        ax[i,0].plot(di.index, di[inpt],"k-", label = inpt,    drawstyle = "steps-post", linewidth  = 1.0)
        if i==0:update_legend(ax[i,0], ["k"],0,1.2,2,True)
        ax[i,0] = ax[i,0].twinx()
        ax[i,0].plot(di.index, di[outp],"r.", label = outp,    drawstyle = "steps-post", markersize = 4.0)
        ax[i,0].plot(di.index, y,       "r-", label = "model", drawstyle = "steps-post", linewidth  = 2.0)
        ax[i,0].set_ylim(min(min(y),di[outp].min()),max(max(y),di[outp].max()))
        if i==0:update_legend(ax[i,0],["r","r"],0.8,1.2,2,True)
        #----------------------------------------------------------------------
        text = F"num: { [round(x,6) for x in tff.num]}\n"  +\
               F"den:  {[int(round(x,0)) for x in tff.den]}\n"  +\
               F"del:   {tff.delay}\n"+\
               F"R2:    {round(tff.R2,2)}"
        ax[i,0].text(di.index[0]+(di.index[-1]-di.index[0])*1.15, 
                     di[outp].max(), 
                     text,ha='left',va='top', 
                     fontweight="bold",fontsize=12,color="white", 
                     bbox=dict(facecolor='firebrick',alpha=0.8,edgecolor='white'))
        #----------------------------------------------------------------------
        lims = []
        for lowSTD_tag in lowSTDdict.keys():
            min_   = data[lowSTD_tag].min()
            max_   = data[lowSTD_tag].max()
            range_ = max_ - min_
            lims.append([min_- 0.05*range_, max_ + 0.05*range_])
        leftax_df      = di[list(lowSTDdict.keys())].iloc[:,:3]
        rightax_df     = di[list(lowSTDdict.keys())].iloc[:,3:]
        leftax_limits  = lims[:3]
        rightax_limits = lims[3:]
        
        multi_yax_plot(ax[i,1],
                       leftax_df=leftax_df,
                       leftax_limits=leftax_limits,
                       rightax_df=rightax_df,
                       rightax_limits=rightax_limits,
                       colors=sns.color_palette("deep", len(lowSTDdict.keys())),linewidth=1)
    plt.show()