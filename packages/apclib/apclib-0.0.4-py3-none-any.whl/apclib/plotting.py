import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def view_fuzzy_design(fuzzy):
    plt.rcParams.update({"lines.color":       "white",
                         "patch.edgecolor":   "white",
                         "text.color":        "white",
                         "axes.edgecolor":    "white",
                         "axes.labelcolor":   "white",
                         "xtick.color":       "white",
                         "ytick.color":       "white",
                         "axes.grid" :         False, 
                         "grid.color":        "lightgray",
                         "axes.facecolor":    "darkslategray",
                         "figure.facecolor":  "k",
                         "figure.edgecolor":  "k",
                         "savefig.facecolor": "k",
                         "savefig.edgecolor": "k",
                         'legend.handlelength':0})
    
    '''
        fuzzy: instance of fuzzy class
    '''
    num_rows = max(len(fuzzy.input.keys()), len(fuzzy.output.keys()))
    if num_rows == 1:num_rows = 2
    
    fig, ax = plt.subplots(num_rows, 3, figsize = (20, num_rows*3))
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    colors = ["b","g","r","c","m","y","k","w"]*100
    colors = ["c","y","tomato"]*100
    
    # Plot input & output memebership functions
    fuzzy.gen_output()    
    for j,io in enumerate([fuzzy.input, fuzzy.output]):
        
        for i,key in enumerate(io.keys()):
            x = fuzzy.gen_xrange(io[key])
            for k,func in enumerate(io[key]["function"]):
                y = [fuzzy.memfunc(inpt  =xi,
                                   func  =io[key]["function"][func]["type"],
                                   limits=io[key]["function"][func]["limits"],
                                   memMax=io[key]["function"][func]["membership_max"]) for xi in x]
                ax[i,j].plot(x,y,color=colors[k],label=func)
                ax[i,j].text(io[key]["value"],
                             io[key]["function"][func]["membership"], 
                             str(round(io[key]["function"][func]["membership"],2)),
                             color="w",fontweight="bold",
                             ha="center", va="center", bbox=dict(facecolor=colors[k],edgecolor='none',pad=1.0))
                if j > 0:
                    y = [fuzzy.memfunc(inpt  =xi,
                                       func  =io[key]["function"][func]["type"],
                                       limits=io[key]["function"][func]["limits"],
                                       memMax=io[key]["function"][func]["membership"]) for xi in x]
                    ax[i,j].fill_between(x,y,color=colors[k],alpha=0.4)
            leg = ax[i,j].legend(loc="upper center", ncol=len(io[key]["function"].keys()),handletextpad=0.,frameon=True)
            for c,l,t in zip(colors,leg.legendHandles,leg.get_texts()):t.set_color(c);t.set_ha('left');t.set_fontweight('bold');l.set_linewidth(0)
            ax[i,j].set_ylim(-0.1,1.55)
            ax[i,j].set_yticks([0,.2,.4,.6,.8,1])
            ax[i,j].plot([io[key]["value"],io[key]["value"]],[0,1],"w--",linewidth=1)
            ax[i,j].text(io[key]["value"], 1.08, str(round(io[key]["value"],2)),fontsize=11,ha="center") 
            title = "INPUT"
            if j > 0: title = "OUTPUT" 
            ax[i,j].set_title(title+": "+key)
            
    # Simulate multiple scenarios
    io_links = {}
    for rule in fuzzy.rules.keys():
        for otpt in fuzzy.rules[rule]["output"].keys():
            if otpt not in io_links.keys():io_links[otpt] = []
            for inpt in fuzzy.rules[rule]["input"].keys():
                if inpt not in io_links[otpt]: io_links[otpt].append(inpt)
    for i,otpt in enumerate(io_links.keys()):
        x = {}
        for inpt,N in zip(io_links[otpt][:2],[50,10]): x[inpt] = fuzzy.gen_xrange(fuzzy.input[inpt],N)
  
        if len(x.keys()) == 1:
            inpt = list(x.keys())[0]
            y = []
            for xi in x[inpt]:
                fuzzy.input[inpt]["value"] = xi
                fuzzy.gen_output()
                y.append(fuzzy.output[otpt]["value"])
            ax[i,2].plot(x[inpt],y,"w",drawstyle="steps-post")
            ax[i,2].set_ylabel("OUTPUT: "+otpt)
            ax[i,2].set_xlabel("INPUT: " +inpt)
        else:
            low_len_key = [(key, len(x[key])) for key in x.keys()]
            low_len_key.sort(key=lambda x: x[1])
            low_len_key, high_len_key  = low_len_key[0][0],low_len_key[1][0]
            
            colors = sns.color_palette("Spectral",len(x[low_len_key]))[::-1]
            y_prev = []
            for k,xi in enumerate(x[low_len_key]):
                fuzzy.input[low_len_key]["value"] = xi
                y = []
                for xii in x[high_len_key]:
                    fuzzy.input[high_len_key]["value"] = xii
                    fuzzy.gen_output()
                    y.append(fuzzy.output[otpt]["value"])
                if k==0 or sum([(abs(yi/np.std(y)-y_previ/np.std(y_prev))) for yi,y_previ in zip(y,y_prev)]) > 1e-10:
                    ax[i,2].plot(x[high_len_key],y,color=colors[k],label=str(round(xi,2)),drawstyle="steps-post")
                    ax[i,2].text(x[high_len_key][int(len(y)*.5)],y[int(len(y)*.5)],str(round(xi,2)),
                                 color=colors[k],fontweight="bold",
                                 ha="center", va="center", bbox=dict(facecolor="k",edgecolor='none',pad=1.0,alpha=1))
                y_prev = y
            ax[i,2].set_ylabel("OUTPUT: "+otpt)
            ax[i,2].set_xlabel("INPUT: " +high_len_key)
            leg = ax[i,2].legend(loc="upper right", 
                                 frameon = False, 
                                 title = "INPUT: " + low_len_key, 
                                 bbox_to_anchor=(1.4, 1.),
                                 ncol=int(len(ax[i,2].lines)>5)+1,
                                 handletextpad=0.)
            for l,t in zip(leg.legendHandles,leg.get_texts()):
                t.set_color(l.get_color())
                t.set_ha('center')
                t.set_fontweight('bold')
                l.set_linewidth(0)
            leg.get_title().set_position((-15, 0))
            leg._legend_box.align = "left"
    
    # Clean empty plots
    for i in range(ax.shape[0]):
        for j in range(ax.shape[1]):
            if len(ax[i,j].lines) == 0:
                fig.delaxes(ax[i,j])

def multi_yax_plot(ax, 
                   leftax_df=pd.DataFrame(),  # left  axis data frame 
                   rightax_df=pd.DataFrame(), # right axis data frame
                   leftax_limits=None,        # options include:
                   rightax_limits=None,       # None | [low,high] | [[low,high], [low,high], [low,high]]
                   leftax_style="-",          # options include:
                   rightax_style="-",         # "-", ".", ".-" | ["-",".",":"]
                   colors="bright",           # "palette" | ["k", "r", "g"]
                   linewidth=None,
                   markersize=None,
                   ylabel_fontsize=15):
    
    def set_spines(ax,which="left",loc=0,color="k"):
        if which!= "host":
            left_right = ["right","left"]
            if which == "left": left_right = ["left","right"]
            ax.spines[left_right[0]].set_position(("axes", loc))
            ax.spines[left_right[0]].set_visible(True)
            ax.spines[left_right[0]].set_linewidth(3)
            ax.spines[left_right[1]].set_visible(False)
            ax.spines["bottom"].     set_visible(False)
            ax.spines["top"].        set_visible(False)
            plt.setp(ax.spines.values(), color=color)
            ax.yaxis.set_label_position(which)
            ax.yaxis.set_ticks_position(which)
            ax.yaxis.label.set_color(color)
            ax.tick_params(axis='y', colors=color,width=2,size=5)
        else:
            ax.axes.get_yaxis().set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(True)
    
    if leftax_limits  is None:leftax_limits =[[None,None] for _ in range(leftax_df. shape[1])]
    if rightax_limits is None:rightax_limits=[[None,None] for _ in range(rightax_df.shape[1])]
    if not any(isinstance(x, list) for x in leftax_limits): leftax_limits =[[leftax_limits[0], leftax_limits[1]] for _ in range(leftax_df. shape[1])]
    if not any(isinstance(x, list) for x in rightax_limits):rightax_limits=[[rightax_limits[0],rightax_limits[1]]for _ in range(rightax_df.shape[1])]
    if not isinstance(leftax_style, list): leftax_style =[leftax_style  for _ in range(leftax_df. shape[1])]
    if not isinstance(rightax_style,list): rightax_style=[rightax_style for _ in range(rightax_df.shape[1])]
    if not isinstance(colors,list): colors = sns.color_palette(colors, leftax_df.shape[1]+rightax_df.shape[1])
    
    set_spines(ax, which="host")
    ax_left  = [ax.twinx() for _ in range(leftax_df. shape[1])]
    ax_right = [ax.twinx() for _ in range(rightax_df.shape[1])]
    
    for i,col in enumerate(leftax_df.columns):
        set_spines(ax_left[i], which="left", loc=-(i*1.2)/plt.gcf().get_size_inches()[0], color=colors[i])
        ax_left[i].set_ylabel(col,fontweight='bold',fontsize=ylabel_fontsize,loc="bottom")
        ax_left[i].plot(leftax_df.index,leftax_df[col],
                        leftax_style[i],color=colors[i],
                        linewidth=linewidth,markersize=markersize,
                        drawstyle="steps-post")
        ax_left[i].set_ylim(leftax_limits[i][0],leftax_limits[i][1])

    if leftax_df.columns.shape[0] == 0: i=0
    for j,col in enumerate(rightax_df.columns):
        set_spines(ax_right[j], which="right", loc=1+j*1.2/plt.gcf().get_size_inches()[0], color=colors[i+j+1])
        ax_right[j].set_ylabel(col,fontweight='bold',fontsize=ylabel_fontsize,loc="bottom")
        ax_right[j].plot(rightax_df.index,rightax_df[col],
                         rightax_style[j],color=colors[i+j+1],
                         linewidth=linewidth,markersize=markersize,
                         drawstyle="steps-post")
        ax_right[j].set_ylim(rightax_limits[j][0],rightax_limits[j][1])
    return ax_left, ax_right

def update_legend(ax, colors=None, x_loc=1.05, y_loc=1, linewidth=2,frameon=False):
    leg = ax.legend(loc = "upper left", bbox_to_anchor=(x_loc, y_loc), 
                    fontsize=10, frameon = frameon, edgecolor = "k", facecolor = "white")

    if colors is not None:
        for i,(c,l,text) in enumerate(zip(colors,leg.legendHandles,leg.get_texts())):
            text.set_color(c)
            l.set_linewidth(linewidth)
    else:
        for l,text in zip(leg.legendHandles,leg.get_texts()):
            try: text.set_color(l.get_color())
            except: continue
            text.set_fontweight('bold')