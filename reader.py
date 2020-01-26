import sys
import numpy as np
#import numpy.ma as ma
import time


import config as cf
import pedestals as ped
import channelmapper as cmap
import read_event as read
import plot_event as plot_ev
import noise_filter as noise


tstart = time.time()
data = open("1323_10_a.cosmics", "rb")

nevent = 5

""" Analysis parameters """
lowpasscut     = 0.1 #MHz    
freqlines      = [0.0234]
signal_thresh  = 3.5
adc_thresh     = 6.
coherent_group = 64


cmap.ChannelMapper()
ped.MapRefPedestal()

""" Reading Run Header """
run_nb, nb_evt = np.fromfile(data, dtype='<u4', count=2)

if(nevent > nb_evt):
    print "only ", nb_evt, " in this file"
    nevent = nb_evt
    
sequence = []
for i in range(nb_evt):
    seq  = np.fromfile( data, dtype='<u4', count=4)
    # 4 uint of [event number - event total size with header- event data size - 0]
    sequence.append(seq[1])

event_pos = []
event_pos.append( data.tell() )
for i in range(nb_evt-1):
    data.seek(sequence[i], 1)
    event_pos.append( data.tell() ) #get the byte position of each event

""" End of run header reading part """



npalldata = np.zeros((2, cf.n_View, cf.n_ChanPerCRP, cf.n_Sample)) #crp, view, vchan


"""
the mask will be used to differentiate background (True for noise processing) from signal (False for noise processing)
at first everything is considered background (all at True)
"""
mask = np.ones((2, cf.n_View, cf.n_ChanPerCRP, cf.n_Sample), dtype=bool)

"""
alive_chan mask intends to not take into account broken channels
True : not broken
False : broken
TO DO : make a run-dependent definition of broken channels
"""

alive_chan = np.ones((2,cf.n_View, cf.n_ChanPerCRP, cf.n_Sample), dtype=bool)
for ibrok in cf.broken_channels:
    crp, view, vch = cmap.DAQToCRP(ibrok)
    alive_chan[crp, view, vch, : ] = False
    

for ievent in range(nevent):
    print "-*-*-*-*-*-*-*-*-*-*-"
    print " READING EVENT ", ievent
    print "-*-*-*-*-*-*-*-*-*-*-"


    tevtread = time.time()
    idx = event_pos[ievent]
    evt, npdatav0, npdatav1 = read.read_event( data, idx)
    evt.evt_nb_loc = ievent
    
    print "RUN ",evt.run_nb, " EVENT ", evt.evt_nb_loc, " / ", evt.evt_nb_glob,
    print " is ", "good " if evt.evt_flag==True else "bad "
    print "Taken at ", time.ctime(evt.time_s), " + ", evt.time_ns, " ns "


    tevtdata = time.time()

    print " -> Reading time %.2f s"%( tevtdata - tevtread)

    if( len(npdatav0)/cf.n_Sample != cf.n_ChanPerView):
        print " PBM OF Nb of CHANNELS in V0 !!! ", len(npdatav0)/cf.n_Sample , " vs ", cf.n_ChanPerView
    if( len(npdatav1)/cf.n_Sample != cf.n_ChanPerView):
        print " PBM OF Nb of CHANNELS in V1 !!! ", len(npdatav1)/cf.n_Sample , " vs ", cf.n_ChanPerView
        

    npdatav0 = np.split(npdatav0, cf.n_ChanPerView)
    npdatav1 = np.split(npdatav1, cf.n_ChanPerView)

    """reset"""
    npalldata[:,:,:,:] = 0.
    mask[:,:,:,:] = True

    
    """reshape the array and subtract reference pedestal"""
    """for noise processing, the reshaping is useless but makes the code readable - change in the future ? """
    
    for idq in range(cf.n_ChanTot):
        crp, view, vch = cmap.DAQToCRP(idq)
        if(crp > 1): continue #Do not care about CRP 2 & 3 ATM
        pedval = ped.GetPed(idq)
        if(crp < 0 or view < 0 or vch < 0):
            print " ERROR ? ", idq
        if(view==0):
            npalldata[crp,view,vch] = npdatav0[idq] - pedval            
        elif(view==1):
            npalldata[crp,view,vch] = npdatav1[idq-3840] - pedval
            
            
    print " done getting event ", ievent, " ! %.2f"%(time.time() - tevtdata)
    
    
    tfft = time.time()
    npalldata = noise.FFTLowPass(npalldata, lowpasscut, freqlines)    
    print " time to fft %.2f"%( time.time() - tfft)
    
    """ 1st ROI attempt based on ADC cut + broken channels """
    mask = np.where( (npalldata > adc_thresh) | ~alive_chan, False, True)

    """ Update ROI based on ped rms """
    mask = noise.define_ROI(npalldata, mask, signal_thresh, 2)
    
    t3 = time.time()
    """Apply coherent filter """
    npalldata = noise.coherent_filter(npalldata, mask, coherent_group)
        
    print " time to coh filt %.2f"%( time.time() - t3)


    t4 = time.time()

    """ Update ROI regions """
    mask = noise.define_ROI(npalldata, mask, signal_thresh, 2)
    print " time to ROI %.2f"%(time.time() - t4)



    ROI = np.array(~mask, dtype=int)
    ROI *= 50
    plot_ev.plot_event_display(npalldata, evt.run_nb, evt.evt_nb_glob,"filt")
    plot_ev.plot_event_display(ROI, evt.run_nb, evt.evt_nb_glob, "ROI")

    ped_rms = noise.get_RMS(npalldata*mask)
    plot_ev.plot_pedestal([ped_rms], ['Final'],['r'], evt.run_nb, evt.evt_nb_glob)


data.close()
tottime = time.time() - tstart
print " TOTAL RUNNING TIME %.2f s == %.2f evt/s"% (tottime, tottime/nevent)