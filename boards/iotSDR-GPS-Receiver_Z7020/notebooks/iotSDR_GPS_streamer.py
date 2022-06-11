from pynq import MMIO
import pynq.lib.dma
from pynq import Xlnk
import numpy as np
import threading
import time
from queue import Queue 

class GPS_RX_Streaming():

    def __init__(self,sample_size=128,overlay=None):
        
        self.lock = threading.Lock()
        self.dma = overlay.GPS_Receiver_IQ_Streamer.axi_dma_0
        self.data_size = sample_size
        
        self.xlnk = Xlnk()
        self.input_buffer = self.xlnk.cma_array(shape=(self.data_size,), dtype=np.uint32)
        self._isFetching = True
        self.blk_count = 0
        
        """GPIO based settings initialization"""
        GPIO_BASE_ADDRESS   = 0x41200000
        GPS_IP_BASE_ADDRESS = 0x41210000
        DMA_IP_BASE_ADDRESS = 0x40400000
        ADDRESS_RANGE       = 0x4
        ADDRESS_OFFSET      = 0x00

        self.FIFORESET_OFFSET       = 16
        self.IQSTREAM_EN_OFFSET     = 20
        self.RFSTREAM_EN_OFFSET     = 24
        self.SAMPLES_PER_BLK_OFFSET = 0
        self.SELECT_TO_FFT_OFFSET = 31


        self.LEDs        = MMIO(GPIO_BASE_ADDRESS, ADDRESS_RANGE)
        self.GpsSettings = MMIO(GPS_IP_BASE_ADDRESS, ADDRESS_RANGE)
        
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.filename = "/home/xilinx/jupyter_notebooks/iotSDR-GPS/rec5s_40960IF"#+timestr
        
        
        """update dma frame size"""
        #self.GpsSettings.write(0x0, self.data_size)

    def tally(self):

        while self._isFetching:
            for i in range(4):
                self.LEDs.write(0, ~(0x1  << i) & 0xF)
                time.sleep(0.1)
        
    def start_streaming(self):

        self.enable_rf_stream(0)
        self.fifo_reset()
        self.enable_iq_stream(1)
        self.enable_rf_stream(1)

    def stream_iq_to_fft(self):
        self.enable_rf_stream(0)
        self.select_iq_for_fft(1)

        self.fifo_reset()
        self.enable_iq_stream(1)
        self.enable_rf_stream(1)

        
    def stop_streaming(self):    
        self.enable_iq_stream(1)
        self.enable_rf_stream(0)
        self.fifo_reset()
        self.select_iq_for_fft(0)

    def set_blk_size(self,val):
            mask = self.GpsSettings.read(0) & 0xFFEFFFFF
            self.GpsSettings.write(0x0, val << self.SAMPLES_PER_BLK_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            #print(hex(status))


    def fifo_reset(self):
            """Active High Reset"""
            mask = self.GpsSettings.read(0) & 0xFFFEFFFF
            self.GpsSettings.write(0x0, 0x1 << self.FIFORESET_OFFSET | mask)
            self.GpsSettings.write(0x0, 0x0 << self.FIFORESET_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            print("reset",hex(status))
        
    def fifo_flush(self):
            """Active High Reset"""
            mask = self.GpsSettings.read(0) & 0xFFFEFFFF
            self.GpsSettings.write(0x0, 0x1 << self.FIFORESET_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            print("flush",hex(status))

    def select_iq_for_fft(self,val):
            mask = self.GpsSettings.read(0) & 0xFFEFFFFF
            self.GpsSettings.write(0x0, val << self.SELECT_TO_FFT_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            #print(hex(status))

    def enable_iq_stream(self,val):
            mask = self.GpsSettings.read(0) & 0xFFEFFFFF
            self.GpsSettings.write(0x0, val << self.IQSTREAM_EN_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            #print(hex(status))

    def enable_rf_stream(self,val):
            mask = self.GpsSettings.read(0) & 0xFEFFFFFF
            self.GpsSettings.write(0x0, val << self.RFSTREAM_EN_OFFSET | mask)
            status = self.GpsSettings.read(0) 
            #print(hex(status))

    def start_fetching(self,file,t=3):
        self.filename = file
        self.start_streaming()
        self._isFetching = True
        self.blk_q = Queue() 
        
        """Threads for gathering dma blocks of samples in background """
        try:
            self.t_sampling  = threading.Thread(target=self.get_time_data,args =(self.blk_q,))
            self.t_file_wrt  = threading.Thread(target=self.write_file,args =(self.blk_q,))
            self.t_led       = threading.Thread(target=self.tally)
            
        except:
            if self.t_sampling.is_alive():
                print('Already thread running')
                self.stop_fecthing()
                self.stop_streaming()

        self.t_file_wrt.start()
        self.t_sampling.start()
        self.t_led.start()  
        
        print("Recording started")
        time.sleep(t)
        self.stop_fetching()

    def stop_fetching(self):
        self._isFetching = False
        self.t_sampling.join()
        self.t_file_wrt.join()
        self.t_led.join()
        self.stop_streaming()

        print("streaming Stop")


    def get_time_data(self,blk_out_q):
        
        self.blk_count = 0
        
        try:
            while self._isFetching: #and blk_count < 2:

                self.dma.recvchannel.transfer(self.input_buffer)
                self.dma.recvchannel.wait()
  
                self.blk_count += 1
                """
                used queue to ensure dma calls not wait enough
                to full the FPGA samples FIFO this is essential
                to ensure the contineuty of samples
                """
                blk_out_q.put(self.input_buffer)
                #print(".",end=" ")

        finally:       
            #End flag for file writing thread
            blk_out_q.put(None)
            print("Recording stoped",self.blk_count)
            
    
    """ Seperate thread to write samples queue
        to file without disturbing the contiuty
        of samples fetching thread. This thread
        ensures that the saved samples are continous.
        which is necessary for GPS acuasition.
        
    """        
    def write_file(self,blk_in_q):

        count = 0
        self.f = open(self.filename,"wb")
        try:
            while True:
                blk = blk_in_q.get()

                #last blk to exit thread
                if blk is None:
                    break

                self.f.write(blk)    
                count +=1
        finally:
            
            self.f.close() 
            time.sleep(0.1)
            print("File writing Complete",count)
        