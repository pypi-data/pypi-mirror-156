class fuzzy:

    def __init__(self):
        self.input  = {}
        self.output = {}
        self.rules  = {}   

    def gen_xrange(self,io, N=100):
        '''
            generates a list of numbers between the min and max limits of all 
            the membership functions for an input|output (io)
            
            io: input[tag] | output[tag]
            N: number of increments
            return: list of number between min and max limits 
        '''
        def f_range(start, stop, inc):
            result = [start]
            while result[-1] < stop:
                result.append(result[-1]+inc)
            return result
        x = []
        for func in io["function"]:
            x.extend(io["function"][func]["limits"])
        x = f_range(min(x),max(x),(max(x)-min(x))/N)
        return x

    def memfunc(self,inpt=1,func="",limits=[0,1,2],memMax=1.):
        ''' inpt:   input
            func:   ltrap - left trapezium
                    rtrap - right trapezium
                    else  - triangle
            limits: func definition limits
            memMax: max allowed degree of membership
            
            return: degree of membership
        '''
        if   func == "ltrap" : return max(min((inpt-limits[2])/(limits[1]-limits[2]),memMax),0) # left trapesium
        elif func == "rtrap" : return max(min((limits[0]-inpt)/(limits[0]-limits[1]),memMax),0) # right trapesium
        elif inpt < limits[1]: return max(min((inpt-limits[0])/(limits[1]-limits[0]),memMax),0) # triangle left side
        else:                  return max(min((limits[2]-inpt)/(limits[2]-limits[1]),memMax),0) # triangle right side

    def gen_input_membership(self):
        '''
            generates input membership for each input on each memebership function
        '''
        for inpt in self.input.keys():
            for func in self.input[inpt]["function"].keys():
                self.input[inpt]["function"][func]["membership"] = self.memfunc(inpt  =self.input[inpt]["value"],
                                                                                func  =self.input[inpt]["function"][func]["type"],
                                                                                limits=self.input[inpt]["function"][func]["limits"],
                                                                                memMax=self.input[inpt]["function"][func]["membership_max"])

    def gen_output_membership(self):
        '''
            generates output membership for each rule on respective output memebership function
        '''
        for rule in self.rules.keys():
            membership = [self.input[inpt]["function"][self.rules[rule]["input"][inpt]]["membership"] for inpt in self.rules[rule]["input"]]
            membership = sum(membership)/float(len(membership))
            for otpt in self.rules[rule]["output"]:
                self.output[otpt]["function"][self.rules[rule]["output"][otpt]]["membership"] = min(membership,
                                                                                                    self.output[otpt]["function"][self.rules[rule]["output"][otpt]]["membership_max"]) 

    def calc_centroid(self):
        '''
            calculate the centroid for each output and assigns 
            it to the "value" key entry 
        '''
        for otpt in self.output.keys():
            x = self.gen_xrange(self.output[otpt])
            y = []
            for func in self.output[otpt]["function"].keys():
                y_ = [self.memfunc(inpt  =xi,
                                   func  =self.output[otpt]["function"][func]["type"],
                                   limits=self.output[otpt]["function"][func]["limits"],
                                   memMax=self.output[otpt]["function"][func]["membership"]) for xi in x]
                y.append(y_)
            y = [max(yi) for yi in zip(*y)]        
            try: self.output[otpt]["value"] = sum(xi*yi for xi,yi in zip(x,y))/sum(y)
            except: pass

    def gen_output(self):
        '''
            for a given set values in the inputs
            the following steps are followed:
            1. Update the input degree of membership for each membership function
            2. For each rule assign the degree of membership for each output
            3. Update the value for each output by calculating the centroid
               from the degree of membership from each membership function
        '''
        self.gen_input_membership()
        self.gen_output_membership()
        self.calc_centroid()

def gain_update(kc_small,kc_large,cv,cv_limits=[None,None,None,None]):
    '''

    ------------------------------------------------
     positive kc
    ------------------------------------------------
    ...lim[0]                 lim[3]...  -> kc_large
             .               .
              .             .
              lim[1]...lim[2]            -> kc_small


    ------------------------------------------------
      negative kc
    ------------------------------------------------
              lim[1]...lim[2]            -> kc_small
              .             .
             .               .
    ...lim[0]                 lim[3]...  -> kc_large

    '''
    if   cv< cv_limits[0] or  cv>cv_limits[3]:return kc_large
    elif cv> cv_limits[1] and cv<cv_limits[2]:return kc_small
    elif cv<=cv_limits[1]:return (kc_small-kc_large)*(cv-cv_limits[1])/(cv_limits[1]-cv_limits[0])+kc_small
    else:                 return (kc_large-kc_small)*(cv-cv_limits[3])/(cv_limits[3]-cv_limits[2])+kc_large

class pidff:

    def __init__(self, cv, sp, mv, mv_min, mv_max, dt, kc, ti, td=0, db=0, dv={}, kf={}):

        '''
         cv      controlled variable
         sp      set point
         mv      manipulated variable
         mv_min  manipulated variable lower limit
         mv_max  manipulated variable upper limit
         dt      sampling rate
         kc      controller gain
         ti      controller integral time constant
         td      controller derivative constant
         db      dead band
         dv      disturbance variable
         kf      feed forward gain (proportional)
        '''
        self.e      = [sp-cv]*3
        self.mv     = mv 
        self.mv_min = mv_min
        self.mv_max = mv_max
        self.dt     = dt
        self.kc     = kc
        self.ti     = ti
        self.td     = td 
        self.db     = db 
        self.dv     = dict(dv)
        self.kf     = dict(kf)

    def update_tune(self, mv_min, mv_max, kc, ti, td=0, db=0, kf={}):
        self.mv_min = mv_min
        self.mv_max = mv_max
        self.kc     = kc
        self.ti     = ti
        self.td     = td 
        self.db     = db 
        self.kf     = kf
        
    def update_mv(self, cv, sp, dv={}):
        self.e=[sp-cv,self.e[0],self.e[1]]
        if (abs(self.e[0]) > self.db*0.5) or self.db==0:                           # take control action if error falls outside deadband
            self.mv += (self.kc*                (self.e[0]-  self.e[1]          )+ #      P
                        self.kc/self.ti*self.dt*(self.e[0]                      )+ #      I
                        self.kc*self.td/self.dt*(self.e[0]-2*self.e[1]+self.e[2])) #      D
        for key in dv.keys():
            self.mv += self.kf[key]*(dv[key]-self.dv[key])                         #      FF
            self.dv[key]=dv[key]

        self.mv = max(min(self.mv,self.mv_max),self.mv_min)                        # clamp mv
        
        return self.mv