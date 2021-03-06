import config as cf
import data_containers as dc


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from matplotlib import collections  as mc
import itertools as itr
import math
import colorcet as cc

from mpl_toolkits.mplot3d import Axes3D 
    
light_blue_red_dict = {
    'red': ((0.,    65./255.,  65./255.),
            (0.15, 123./255., 123./255.),
            (0.25, 160./255., 160./255.),
            (0.375, 222./255.,222./255.),
            (0.5, 214./255., 214./255.),
            (0.625, 199./255., 199./255.),
            (0.75, 183./255., 183./255.),
            (0.875, 153./255., 153./255.),
            (1., 78./255., 78./255.)),

    'green':  ((0.,  90./255.,  90./255.),
              (0.15, 171./255., 171./255.),
              (0.25,  211./255., 211./255.),
              (0.375,  220./255.,  220./255.),
              (0.5, 190./255., 190./255.),
              (0.625,  132./255., 132./255.),
              (0.75,  65./255.,  65./255.),
              (0.875, 0./255., 0./255.),
               (1.,  0./255., 0./255.)),
        
    
    
    'blue':   ((0.,  148./255., 148./255.),
               (0.15, 228./255., 228./255.),
               (0.25, 222./255., 222./255.),
               (0.375,  160./255.,  160./255.),
               (0.5, 105./255., 105./255.),
               (0.625, 60./255., 60./255.),
               (0.75, 34./255., 34./255.),
               (0.875, 0./255., 0./255.),
               (1.,  0./255., 0./255.))
    
}
lbr_cmp = LinearSegmentedColormap('lightBR', light_blue_red_dict)
cmap_nice = cc.cm.linear_tritanopic_krjcw_5_95_c24_r


adcmin = -10#10
adcmax = 30#10 #35


def plot_waveform(data, legtitle, colors, option=None):

    nplot = len(data)
    print(nplot)
    if(nplot > 9):
        print(" ooops, I will only plot 9 waveforms")

    fig = plt.figure(figsize=(12,9))
    ax = []

    for ip in range(nplot):
        ax.append(fig.add_subplot(nplot,1,ip+1))#, sharex=True))
        d = data[ip]                
        plt.plot(d, colors[ip], label=legtitle[ip])
        ax[-1].set_xlabel('Time [tdc]')
        ax[-1].set_ylabel('ADC')
        #ax[-1].set_ylim(-8., 35.)
        plt.legend()
        plt.subplots_adjust(bottom=0.05, top=.98, hspace=0.27)



    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/waveform'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    plt.close()    



def plot_waveform_evo(data, legtitle, colors, option=None):

    nplot = len(data[0])
    nstep = len(data)
    if(nplot > 9):
        print(" ooops, I will only plot 9 waveforms")
        nplot = 9

    fig = plt.figure(figsize=(12,9))
    ax = []

    for ip in range(nplot):
        ax.append(fig.add_subplot(nplot,1,ip+1))#, sharex=True))
        for iev in range(nstep):
            d = data[iev][ip]    
            plt.plot(d, colors[iev], label=legtitle[iev])
            ax[-1].set_xlabel('Time [tdc]')
            ax[-1].set_ylabel('ADC')
            ax[-1].set_ylim(-8., 35.)
        plt.legend()
    plt.subplots_adjust(bottom=0.05, top=.98, hspace=0.27)



    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/waveform_evolution'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()    




def plot_waveform_hits(crp, view, channel, nsig, option=None):

    fig = plt.figure(figsize=(12,3))
    ax = []
    tdc = np.arange(0,10000,1)    
    wvf = dc.data[crp,view,channel,:]
    hit_start = [x.start for x in dc.hits_list if x.view == view and x.crp == crp and x.channel == channel]
    hit_stop = [x.stop for x in dc.hits_list if x.view == view and x.crp == crp and x.channel == channel]

    plt.plot(tdc, wvf, c='black')
    pedmean = dc.ped_mean[crp, view, channel]
    pedrms = dc.ped_rms[crp, view, channel]
    thr = nsig * pedrms
    
    plt.plot([0,10000],[thr,thr], linestyle="--", color="red")
    

    for f, t in zip(hit_start, hit_stop):
        plt.plot(tdc[f:t+1], wvf[f:t+1], marker=".")


    plt.plot([0,10000],[pedmean,pedmean], color="cyan")
    plt.plot([0,10000],[pedmean+pedrms, pedmean+pedrms], linestyle="dotted", color="cyan")
    plt.plot([0,10000],[pedmean-pedrms, pedmean-pedrms], linestyle="dotted", color="cyan")


    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/waveform_hits'+option+'_run_'+run_nb+'_evt_'+evt_nb+'_crp'+str(crp)+'_v'+str(view)+'_ch'+str(channel)+'.png')
    #plt.show()
    plt.close()    



def plot_event_display(option=None):    

    fig = plt.figure(figsize=(12,9))
    gs = gridspec.GridSpec(nrows=3,ncols=2, height_ratios=[1,15,15])
    axv0 = []
    axv1 = []
    im = []

    i = 1

    for icrp in range(2):
        for iview in range(2):
            axv0.append(fig.add_subplot(gs[i, 0]))
            im.append(plt.imshow(dc.data[icrp,0,:,:].transpose(), origin='lower',aspect='auto',cmap=cmap_nice, vmin=adcmin, vmax=adcmax))        
            if(icrp==1):
                axv0[-1].set_xlabel('View Channel')
            axv0[-1].set_ylabel('Time')
            axv0[-1].set_title('CRP '+str(icrp)+' - View 0')

            """ view 1 """
            axv1.append(fig.add_subplot(gs[i, 1], sharey=axv0[-1]))
            im.append(plt.imshow(dc.data[icrp,1,:,:].transpose(), origin='lower',aspect='auto',cmap=cmap_nice, vmin=adcmin, vmax=adcmax))        
            axv1[-1].yaxis.tick_right()
            axv1[-1].yaxis.set_label_position("right")

            if(icrp==1):
                axv1[-1].set_xlabel('View Channel')
            axv1[-1].set_ylabel('Time')
            axv1[-1].set_title('CRP '+str(icrp)+' - View 1')
        i += 1

    ax_col  = fig.add_subplot(gs[0, :])
    ax_col.set_title('Collected Charge [ADC]')
        
                         
    cb = fig.colorbar(im[0], cax=ax_col, orientation='horizontal')
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')


    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)

    plt.subplots_adjust(wspace=0.05, hspace=0.3, top=0.92, bottom=0.08, left=0.06, right=0.94)
    plt.savefig('ED/ed'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')

    #plt.show()
    plt.close()



def plot_event_display_allcrp(option=None):
    fig = plt.figure(figsize=(12,9))
    gs = gridspec.GridSpec(nrows=4,ncols=2, height_ratios=[1,10,10,10])
    axv0 = []
    axv1 = []
    im = []
    
    i = 1

    for icrp in range(4):
        if(icrp==2): continue
        """ view 0 """
        axv0.append(fig.add_subplot(gs[i, 0]))
        im.append(plt.imshow(dc.data[icrp,0,:,:].transpose(), origin='lower',aspect='auto',cmap=cmap_nice, vmin=adcmin, vmax=adcmax))        
        if(icrp==3):
            axv0[-1].set_xlabel('View Channel')
        axv0[-1].set_ylabel('Time')
        axv0[-1].set_title('CRP '+str(icrp)+' - View 0')

        """ view 1 """
        axv1.append(fig.add_subplot(gs[i, 1], sharey=axv0[-1]))
        im.append(plt.imshow(dc.data[icrp,1,:,:].transpose(), origin='lower',aspect='auto',cmap=cmap_nice, vmin=adcmin, vmax=adcmax))        
        axv1[-1].yaxis.tick_right()
        axv1[-1].yaxis.set_label_position("right")

        if(icrp==3):
            axv1[-1].set_xlabel('View Channel')
        axv1[-1].set_ylabel('Time')
        axv1[-1].set_title('CRP '+str(icrp)+' - View 1')
        i += 1
    ax_col  = fig.add_subplot(gs[0, :])
    ax_col.set_title('Collected Charge [ADC]')
        
                         
    cb = fig.colorbar(im[0], cax=ax_col, orientation='horizontal')
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')

    plt.subplots_adjust(wspace=0.05, hspace=0.4, top=0.92, bottom=0.08, left=0.06, right=0.94)


    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)

    plt.savefig('ED/ed_allcrp'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')

    #plt.show()
    plt.close()


def plot_pedestal(datas, legtitle, colors, option=None):

    nplot = len(datas)

    fig = plt.figure(figsize=(12,9))
    ax = []
    iplot = 0

    for icrp in range(2):
        for iview in range(2):

            iplot = iplot + 1
            ax.append(fig.add_subplot(2,2,iplot))

            for ip in range(nplot):
                d = datas[ip]                
                plt.plot(d[icrp, iview,:], colors[ip], label=legtitle[ip])

            ax[-1].set_xlabel('View Channel')
            ax[-1].set_ylabel('Pedestal RMS (ADC)')
            ax[-1].set_title('CRP '+str(icrp)+' - View '+str(iview))  

            ax[-1].set_ylim(0., 6.)
            plt.legend()

    plt.subplots_adjust(bottom=0.08, top=0.95)


    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/pedrms'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()



def plot_event_fft(data, zmax=1.25, option=None):    

    fig = plt.figure(figsize=(12,9))
    ax = []
    im = []
    iplot = 0


    for icrp in range(2):
        for iview in range(2):
            iplot += 1

            ax.append(fig.add_subplot(2,2,iplot))

            im.append(plt.imshow(data[icrp,iview,:,:].transpose(), origin='lower',aspect='auto',cmap=lbr_cmp, extent=[0, 959, 0., 1.25], vmin=0.))

            plt.colorbar(im[-1])

            plt.ylim(0.,zmax)
            #plt.ylim(0.06, 0.08)

            ax[-1].set_xlabel('View Channel')
            ax[-1].set_ylabel('Signal Frequencies [MHz]')
            ax[-1].set_title('CRP '+str(icrp)+' - View '+str(iview))    

    plt.subplots_adjust(bottom=0.08, top=0.95)


    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)



    plt.savefig('ED/fft'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    plt.show()
    plt.close()



    
def plot_hits_clustered(option=None):

    fig = plt.figure(figsize=(12,9))
    ax  = []
    iplot=0

    for icrp in range(4):
        if(icrp==2): continue
        for iview in range(2):
            iplot += 1
            ax.append(fig.add_subplot(3,2,iplot))
            
            hit_pos = [x.X for x in dc.hits_list if x.view == iview and x.crp == icrp]
            hit_tdc = [x.Z for x in dc.hits_list if x.view == iview and x.crp == icrp]
            hit_cls = [x.cluster for x in dc.hits_list if x.view == iview and x.crp == icrp]

            

            colors = np.array(list(itr.islice(itr.cycle(['#377eb8', '#ff7f00', '#4daf4a',
                                                         '#f781bf', '#a65628', '#984ea3',
                                                         '#79f2ff', '#e41a1c', '#dede00']),
                                              int(dc.evt_list[-1].nClusters[icrp,iview] + 1))))

            # add grey color for outliers (if any)
            colors = np.append(colors, ["#c7c7c7"])

            
            ax[-1].scatter(hit_pos, hit_tdc, c=colors[hit_cls],s=2)
            
            #ax[-1].set_xlim(0,959)
            ax[-1].set_ylim(-30, 300)
            ax[-1].set_xlabel('Position [cm]')
            ax[-1].set_ylabel('Z [cm]')
            ax[-1].set_title('CRP '+str(icrp)+' - View '+str(iview))    
            
            print("CRP ", icrp, " View ", iview, " -> Nhits : ", len(hit_tdc))

    plt.subplots_adjust(bottom=0.08, top=0.95, hspace=0.4)
    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/hit'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()


def plot_hits_var(option=None):

    fig = plt.figure(figsize=(12,9))
    ax  = []
    
    
    ax.append(fig.add_subplot(3,2,1))
    charge = [x.charge for x in dc.hits_list]
    ax[-1].hist(charge, 200, color='orange', histtype="stepfilled", edgecolor='r',log=True,range=(0., 5000.))
    ax[-1].set_xlabel('Hit charge [ADC]')

    ax.append(fig.add_subplot(3,2,2))
    tmax = [x.max_t for x in dc.hits_list]
    ax[-1].hist(tmax, 250, color='c',histtype='stepfilled',edgecolor='b',range=(0, 10000))
    ax[-1].set_xlabel('Hit Time [tdc]')

    ax.append(fig.add_subplot(3,2,3))
    dt = [x.stop-x.start for x in dc.hits_list]
    ax[-1].hist(dt, 200, color='b',histtype='stepfilled',edgecolor='k',log=True, range=(0., 200.))
    ax[-1].set_xlabel('Hit Length [tdc]')

    ax.append(fig.add_subplot(3,2,4))
    amp = [x.max_adc for x in dc.hits_list]
    ax[-1].hist(amp, 200, color='r',histtype='stepfilled',edgecolor='k',log=True, range=(0., 60.))
    ax[-1].set_xlabel('Hit Amplitude [ADC]')

    ax.append(fig.add_subplot(3,2,5))
    dtstart = [x.max_t-x.start for x in dc.hits_list]
    ax[-1].hist(dtstart, 50, color='y',histtype='stepfilled',edgecolor='k',log=True,range=(0., 50))
    ax[-1].set_xlabel('Hit start-max [tdc]')

    ax.append(fig.add_subplot(3,2,6))
    dtstop = [x.stop-x.max_t for x in dc.hits_list]
    ax[-1].hist(dtstop, 50, color='g',histtype='stepfilled',edgecolor='k',log=True,range=(0.,50.))
    ax[-1].set_xlabel('Hit max-stop [tdc]')


    plt.subplots_adjust(bottom=0.08, top=0.95, hspace=0.3)
    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)

    plt.savefig('ED/hit_properties_'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()
    



def plot_hits_view(option=None):

    fig = plt.figure(figsize=(12,6))
    gs = gridspec.GridSpec(nrows=2, ncols=2, height_ratios=[1,30], width_ratios=[6,4])

    ax_col = fig.add_subplot(gs[0,:])
    ax_v0 = fig.add_subplot(gs[1, 0])
    ax_v1 = fig.add_subplot(gs[1, 1], sharey=ax_v0)

    max_adc_range=50
    hit_x_v0 = [x.X for x in dc.hits_list if x.view == 0]
    hit_z_v0 = [x.Z for x in dc.hits_list if x.view == 0]
    hit_q_v0 = [x.max_adc for x in dc.hits_list if x.view == 0]


    hit_x_v1 = [x.X for x in dc.hits_list if x.view == 1]
    hit_z_v1 = [x.Z for x in dc.hits_list if x.view == 1]
    hit_q_v1 = [x.max_adc for x in dc.hits_list if x.view == 1]

    sc0 = ax_v0.scatter(hit_x_v0, hit_z_v0, c=hit_q_v0, cmap=lbr_cmp, s=2, vmin=0, vmax=max_adc_range)

    ax_v0.set_title('View 0')
    ax_v0.set_ylabel('Z [cm]')
    ax_v0.set_xlabel('X [cm]')
    ax_v0.set_xlim([-300., 300])
    ax_v0.set_ylim([-30., 300])

    sc1 = ax_v1.scatter(hit_x_v1, hit_z_v1, c=hit_q_v1, cmap=lbr_cmp, s=2,vmin=0,vmax=max_adc_range)
    ax_v1.set_title('View 1')
    #ax_v1.set_ylabel('Z [cm]')
    ax_v1.set_xlabel('Y [cm]')
    ax_v1.set_xlim([-100,300])
    ax_v1.set_ylim([-30., 300])
    ax_col.set_title('Hit Max ADC')
    cb = fig.colorbar(sc1, cax=ax_col, orientation='horizontal')
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')
    
    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/hit_view'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()

def plot_tracks2D(option=None):

    fig = plt.figure(figsize=(12,6))
    gs = gridspec.GridSpec(nrows=2, ncols=2, height_ratios=[1,30], width_ratios=[6,4])#, height_ratios=[1,10])

    ax_leg = fig.add_subplot(gs[0,:])
    ax_v0 = fig.add_subplot(gs[1, 0])
    ax_v1 = fig.add_subplot(gs[1, 1], sharey=ax_v0)

    #max_adc_range=50
    hit_x_v0 = [x.X for x in dc.hits_list if x.view == 0]
    hit_z_v0 = [x.Z for x in dc.hits_list if x.view == 0]


    hit1_x_v0 = [x.X for x in dc.hits_list if x.view == 0 and x.matched==1]
    hit1_z_v0 = [x.Z for x in dc.hits_list if x.view == 0 and x.matched==1]

    hit2_x_v0 = [x.X for x in dc.hits_list if x.view == 0 and x.matched==2]
    hit2_z_v0 = [x.Z for x in dc.hits_list if x.view == 0 and x.matched==2]

    hit_x_v0_noise = [x.X for x in dc.hits_list if x.view == 0 and x.cluster==-1]
    hit_z_v0_noise = [x.Z for x in dc.hits_list if x.view == 0 and x.cluster==-1]

    tracks_hits_x_v0 = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==0]
    tracks_hits_z_v0 = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==0]



    hit_x_v1 = [x.X for x in dc.hits_list if x.view == 1 ]
    hit_z_v1 = [x.Z for x in dc.hits_list if x.view == 1 ]


    hit1_x_v1 = [x.X for x in dc.hits_list if x.view == 1 and x.matched==1]
    hit1_z_v1 = [x.Z for x in dc.hits_list if x.view == 1 and x.matched==1]

    hit2_x_v1 = [x.X for x in dc.hits_list if x.view == 1 and x.matched==2]
    hit2_z_v1 = [x.Z for x in dc.hits_list if x.view == 1 and x.matched==2]

    hit_x_v1_noise = [x.X for x in dc.hits_list if x.view == 1 and x.cluster==-1]
    hit_z_v1_noise = [x.Z for x in dc.hits_list if x.view == 1 and x.cluster==-1]

    tracks_hits_x_v1 = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==1]
    tracks_hits_z_v1 = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==1]



    ax_v0.scatter(hit_x_v0, hit_z_v0, c="#ffb77d", s=2, label="Hits Clustered")#ffb77d

    ax_v0.scatter(hit1_x_v0, hit1_z_v0, c="#28568f", s=2, label="Hits Attached to track")#ffb77d
    ax_v0.scatter(hit2_x_v0, hit2_z_v0, c="#abdf7f", s=2, label="Hits Attached to track")#ffb77d

    ax_v0.scatter(hit_x_v0_noise, hit_z_v0_noise, c="#d8cfd6", s=2, label="Noise Hits")
    
    #just for the legend
    ax_v0.plot(tracks_hits_x_v0[0],tracks_hits_z_v0[0], c="#de425b",linewidth=1, label="Reconstructed 2D track")

    for tx,tz in zip(tracks_hits_x_v0, tracks_hits_z_v0):
        #ax_v0.scatter(tx, tz, c="#28568f",s=2) ##6d40cf
        ax_v0.plot(tx,tz, c="#de425b",linewidth=1)#f65789

    

    ax_v0.set_title('View 0')
    ax_v0.set_ylabel('Z [cm]')
    ax_v0.set_xlabel('X [cm]')
    ax_v0.set_xlim([-300., 300])
    ax_v0.set_ylim([-30., 300])

    ax_v1.scatter(hit_x_v1, hit_z_v1, c="#ffb77d", s=2)#ffb77d

    ax_v1.scatter(hit1_x_v1, hit1_z_v1, c="#28568f", s=2)#ffb77d
    ax_v1.scatter(hit2_x_v1, hit2_z_v1, c="#abdf7f", s=2)#ffb77d

    ax_v1.scatter(hit_x_v1_noise, hit_z_v1_noise, c="#d8cfd6", s=2)

    for tx,tz in zip(tracks_hits_x_v1, tracks_hits_z_v1):
        #ax_v1.scatter(tx, tz, c="#28568f",s=2)#6d40cf
        ax_v1.plot(tx,tz, c="#de425b",linewidth=1)#f65789


    ax_v1.set_title('View 1')
    ax_v1.set_xlabel('Y [cm]')
    ax_v1.set_xlim([-100,300])
    ax_v1.set_ylim([-30., 300])
    
    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)

    leg = ax_leg.legend(*ax_v0.get_legend_handles_labels(), loc='center', ncol=5, markerscale=4, markerfirst=True)
    for line in leg.get_lines():
        line.set_linewidth(3)
    ax_leg.axis('off')

    plt.savefig('ED/track2D'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()


def plot_tracks3D_proj(option=None):

    fig = plt.figure(figsize=(12,6))
    gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[6,4])

    #ax_col = fig.add_subplot(gs[0,:])
    ax_v0 = fig.add_subplot(gs[0, 0])
    ax_v1 = fig.add_subplot(gs[0, 1], sharey=ax_v0)

    hit_x_v0 = [x.X for x in dc.hits_list if x.view == 0]
    hit_z_v0 = [x.Z for x in dc.hits_list if x.view == 0]

    hit_x_v0_noise = [x.X for x in dc.hits_list if x.view == 0 and x.cluster==-1]
    hit_z_v0_noise = [x.Z for x in dc.hits_list if x.view == 0 and x.cluster==-1]

    tracks_hits_x_v0 = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==0]
    tracks_hits_z_v0 = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==0]
    tracks_hits_x_v0_match = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==0 and t.matched >=0]
    tracks_hits_z_v0_match = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==0 and t.matched>=0]

    #tracks_match_v0  = [["#ad37ad" if t.matched < 0 else "#bd384d" for p in t.path] for t in dc.tracks2D_list if t.view == 0]


    hit_x_v1 = [x.X for x in dc.hits_list if x.view == 1]
    hit_z_v1 = [x.Z for x in dc.hits_list if x.view == 1]

    hit_x_v1_noise = [x.X for x in dc.hits_list if x.view == 1 and x.cluster==-1]
    hit_z_v1_noise = [x.Z for x in dc.hits_list if x.view == 1 and x.cluster==-1]

    tracks_hits_x_v1 = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==1]
    tracks_hits_z_v1 = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==1]
    tracks_hits_x_v1_match = [[p[0] for p in t.path] for t in dc.tracks2D_list if t.view==1 and t.matched>=0]
    tracks_hits_z_v1_match = [[p[1] for p in t.path] for t in dc.tracks2D_list if t.view==1 and t.matched >=0]
    #tracks_match_v1  = [["#ad37ad" if t.matched < 0 else "#bd384d" for p in t.path] for t in dc.tracks2D_list if t.view == 1]


    #trk_colors=np.array([["#ad37ad"], ["#bd384d"]])

    ax_v0.scatter(hit_x_v0, hit_z_v0, c="#ffb77d", s=2)#ffb77d
    ax_v0.scatter(hit_x_v0_noise, hit_z_v0_noise, c="#d8cfd6", s=2)
    

    for tx,tz in zip(tracks_hits_x_v0, tracks_hits_z_v0):
        ax_v0.scatter(tx, tz, c="#28568f",s=2) ##6d40cf
        ax_v0.plot(tx,tz, c="#de255b",linewidth=1)#f65789
    for tx,tz in zip(tracks_hits_x_v0_match, tracks_hits_z_v0_match):
        ax_v0.plot(tx,tz, c="#00a9b2",linewidth=2)#f65789

    ax_v0.set_title('View 0')
    ax_v0.set_ylabel('Z [cm]')
    ax_v0.set_xlabel('X [cm]')
    ax_v0.set_xlim([-300., 300])
    ax_v0.set_ylim([-30., 300])

    ax_v1.scatter(hit_x_v1, hit_z_v1, c="#ffb77d", s=2)#ffb77d
    ax_v1.scatter(hit_x_v1_noise, hit_z_v1_noise, c="#d8cfd6", s=2)



    for tx,tz in zip(tracks_hits_x_v1, tracks_hits_z_v1):
        ax_v1.scatter(tx, tz, c="#28568f",s=2)#6d40cf
        ax_v1.plot(tx,tz, c="#de425b",linewidth=1)#f65789

    for tx,tz in zip(tracks_hits_x_v1_match, tracks_hits_z_v1_match):
        ax_v1.plot(tx,tz, c="#00a9b2",linewidth=2)#f65789

    ax_v1.set_title('View 1')
    ax_v1.set_xlabel('Y [cm]')
    ax_v1.set_xlim([-100,300])
    ax_v1.set_ylim([-30., 300])
    
    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/track3D_proj'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()


def plot_tracks3D(option=None):

    fig = plt.figure(figsize=(12,6))
    ax  = fig.add_subplot(111, projection='3d')

    xv0 = [[p[0] for p in t.path_v0] for t in dc.tracks3D_list]
    yv0 = [[p[1] for p in t.path_v0] for t in dc.tracks3D_list]
    zv0 = [[p[2] for p in t.path_v0] for t in dc.tracks3D_list]

    xv1 = [[p[0] for p in t.path_v1] for t in dc.tracks3D_list]
    yv1 = [[p[1] for p in t.path_v1] for t in dc.tracks3D_list]
    zv1 = [[p[2] for p in t.path_v1] for t in dc.tracks3D_list]

    for i in range(len(xv0)):
        ax.scatter(xv0[i], yv0[i], zv0[i], c='c', s=2)
        ax.scatter(xv1[i], yv1[i], zv1[i], c='orange', s=2)


    ax.set_xlim3d(-300, 300)
    ax.set_ylim3d(0, 300)
    ax.set_zlim3d(-30, 300)
    
    ax.set_xlabel('View 0/X [cm]')
    ax.set_ylabel('View 1/Y [cm]')
    ax.set_zlabel('Drift/Z [cm]')


    if(option):
        option = "_"+option
    else:
        option = ""


    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)


    plt.savefig('ED/track3D'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.show()
    plt.close()



def plot_correlations(data,option=None):

    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)



    gs = gridspec.GridSpec(nrows=1, ncols=3)#, height_ratios=[1,5,5])
    fig = plt.figure(figsize=(12,5))
    ax = []
    ax.append(fig.add_subplot(gs[0, 0]))
    ax[-1].imshow(data, origin='lower',aspect='auto', cmap=lbr_cmp, vmin=-5,vmax=5,interpolation='none')

    ax.append(fig.add_subplot(gs[0, 1]))
    ax[-1].imshow(np.corrcoef(data), origin='lower',aspect='auto', cmap='coolwarm', vmin=-1,vmax=1,interpolation='none')

    ax.append(fig.add_subplot(gs[0, 2]))
    ax[-1].imshow(np.corrcoef(data.transpose()), origin='lower',aspect='auto', cmap='coolwarm', vmin=-1,vmax=1,interpolation='none')
    plt.savefig('ED/micro_correlation_'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    plt.close()


def plot_correlations_all(option=None):

    if(option):
        option = "_"+option
    else:
        option = ""

    run_nb = str(dc.evt_list[-1].run_nb)
    evt_nb = str(dc.evt_list[-1].evt_nb_glob)



    fig_t = plt.figure(1, figsize=(12,6))

    alive_data = dc.data * dc.alive_chan
    all_data_crp0 = np.concatenate((alive_data[0,0,:,:], alive_data[0,1,:,:]))
    all_data_crp1 = np.concatenate((alive_data[1,0,:,:], alive_data[1,1,:,:]))

    print("all data ", all_data_crp0.shape, " and ", all_data_crp1.shape)
    
    corr_t_crp0 = np.corrcoef(all_data_crp0)
    corr_t_crp1 = np.corrcoef(all_data_crp1)

    print("time corr  ", corr_t_crp0.shape, " and ", corr_t_crp1.shape)    

    ax_t_0 = fig_t.add_subplot(121)
    im0_c_t = ax_t_0.imshow(corr_t_crp0, origin='lower',aspect='auto', cmap='coolwarm',vmin=-1,vmax=1,interpolation='none')#,extent=[0,960,0,960])
    cb0_c_t = plt.colorbar(im0_c_t,ax=ax_t_0)
    ax_t_0.set_title('CRP 0')

    ax_t_1 = fig_t.add_subplot(122)
    im1_c_t = ax_t_1.imshow(corr_t_crp1, origin='lower',aspect='auto', cmap='coolwarm',vmin=-1,vmax=1,interpolation='none')#,extent=[0,960,0,960])
    cb1_c_t = plt.colorbar(im1_c_t,ax=ax_t_1)
    ax_t_1.set_title('CRP 1')

    fig_t.savefig('ED/time_correlation'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')
    #plt.close(fig_t)

    fig_s = plt.figure(2, figsize=(12,6))

    all_data_crp0_tr = all_data_crp0.transpose()
    all_data_crp1_tr = all_data_crp1.transpose()

    print("transposed all data ", all_data_crp0_tr.shape, " and ", all_data_crp1_tr.shape)
    
    corr_s_crp0 = np.corrcoef(all_data_crp0_tr)
    corr_s_crp1 = np.corrcoef(all_data_crp1_tr)

    print("space corr  ", corr_s_crp0.shape, " and ", corr_s_crp1.shape)        

    ax_s_0 = fig_s.add_subplot(121)
    im0_c_s = ax_s_0.imshow(corr_s_crp0, origin='lower',aspect='auto', cmap='coolwarm',vmin=-1,vmax=1,interpolation='none')#,extent=[0,960,0,960])
    cb0_c_s = plt.colorbar(im0_c_s,ax=ax_s_0)
    ax_s_0.set_title('CRP 0')

    ax_s_1 = fig_s.add_subplot(122)
    im1_c_s = ax_s_1.imshow(corr_s_crp1, origin='lower',aspect='auto', cmap='coolwarm',vmin=-1,vmax=1,interpolation='none')#,extent=[0,960,0,960])
    cb1_c_s = plt.colorbar(im1_c_s,ax=ax_s_1)
    ax_s_1.set_title('CRP 1')


    fig_s.savefig('ED/space_correlation'+option+'_run_'+run_nb+'_evt_'+evt_nb+'.png')


    plt.close('all')
