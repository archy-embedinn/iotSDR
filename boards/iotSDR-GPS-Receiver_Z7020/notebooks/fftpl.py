"""
// Copyright 2021 embedINN Pvt Ltd
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


GPS MAX2769 RF frontend driver
author: embedinn.com
"""    
from pynq import Xlnk
import numpy as np
import time

class FFTPL(object):

    def __init__(self,overlay,N=32768):
        
        self.N      = N
        self.xlnk   = Xlnk()
        self.fft_data = overlay.fft_data_accelerator.axi_dma_data_fft
        self.fft_config = overlay.fft_data_accelerator.axi_dma_fft_config

    def get_config_value(self,forwards, scaling_sched):
        val = 0
        for scaling in scaling_sched:     # [14:1] = scaling schedule
            val = (val << 2) + scaling

        print(hex(val))
        return (val << 1) + int(forwards) # [0] = direction

    def fft_config_update(self,forwards):
        if forwards:
            config_value = self.get_config_value(forwards, [1,2, 2, 2, 2, 2, 2, 2])
        else:
            config_value = self.get_config_value(forwards, [0,0, 0, 0, 0, 0, 0, 0])

        fft_buffer_config = self.xlnk.cma_array(shape=(1,),dtype=np.int32)
        fft_buffer_config[0] = config_value
        self.fft_config.sendchannel.transfer(fft_buffer_config)
        self.fft_config.sendchannel.wait()
        
    def interleave_iq(self,signal):
        print(signal)
        sig = np.copy(signal)
        i = np.array(sig.real,np.int16)
        q = np.array(sig.imag,np.int16)
        iq = np.concatenate([i,q])
        iq[::2] = i
        iq[1::2] = q
        print(iq)

        return iq

    def deinterleave_iq(self,signal):
        return signal[0::2]+1j*signal[1::2]
      

    def fft_iq_samples(self):
    
        #fft_in_buffer = self.xlnk.cma_array(shape=(self.N*2,),dtype=np.int16)
        fft_out_buffer = self.xlnk.cma_array(shape=(self.N*2,),dtype=np.int16)

        fft_out = np.zeros(len(fft_out_buffer))

        #for i in range(0,max_iters):
            #tic = time.time()
        #np.copyto(fft_in_buffer,signal[self.N*0:2*(self.N*(0+1))])
        tic = time.time()
        #fft_data.sendchannel.transfer(fft_in_buffer)
        self.fft_data.recvchannel.transfer(fft_out_buffer)

        #self.fft_data.sendchannel.wait()
        self.fft_data.recvchannel.wait()
        toc = time.time()
        fft_out = np.array(fft_out_buffer)
        print(fft_out_buffer)
        print(fft_out)

        delta =  "{:.20f}".format((toc-tic)*1000000)
        print("FFT Time(uSec):", delta)
        fft_out_buffer.close()
        #fft_in_buffer.close()

        return fft_out   
    
    def fft_ps_samples(self,samples):
    
        fft_in_buffer = self.xlnk.cma_array(shape=(self.N*2,),dtype=np.int16)
        fft_out_buffer = self.xlnk.cma_array(shape=(self.N*2,),dtype=np.int16)

        fft_out = np.zeros(len(fft_out_buffer))

        np.copyto(fft_in_buffer,samples[self.N*0:2*(self.N*(0+1))])
        tic = time.time()
        
        self.fft_data.sendchannel.transfer(fft_in_buffer)
        self.fft_data.recvchannel.transfer(fft_out_buffer)

        self.fft_data.sendchannel.wait()
        self.fft_data.recvchannel.wait()
        
        toc = time.time()
        fft_out = np.array(fft_out_buffer)

        delta =  "{:.20f}".format((toc-tic)*1000000)
        print("FFT Time(uSec):", delta)
        fft_out_buffer.close()
        fft_in_buffer.close()

        return fft_out   