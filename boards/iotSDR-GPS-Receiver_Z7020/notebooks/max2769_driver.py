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

import iotSDR.max2769_defs as max2769_defs
import spidev


class MAX2769(object):

    def __init__(self,SPIchannel=2):
        
        self.SPIchannel = SPIchannel
        self.spi        = spidev.SpiDev()
        
        ## Default MAX settings
        self.spi_init()
        self.gps_0IF_config()
        
    def spi_init(self):
            """
            Initialize the SPI modules.
            :return: nothing
            """
            self.spi.open(self.SPIchannel, 0)
            self.spi.max_speed_hz = 7800000

    def int32_to_int8(self,n):
        mask = (1 << 8) - 1
        return [(n >> k) & mask for k in range(0, 32, 8)]

    def gps_write_spi(self, address, value=None):
            """
            GPS Register Settings
            
            :param address: the reg addr to be written, last 4 bits
            :param value:   the value to be written first, xfer2 needs 
                            bytes list so some convesion logic applied 
            :return: nothing
            """
            reg = (value << 4) & 0xFFFFFFF0
            reg |= (address & 0x0F)
            
            reg_byte_list = self.int32_to_int8(reg)
            reg_byte_list.reverse()

            self.spi.xfer2(reg_byte_list)       
            
     
    def gps_4096IF_config(self):
        addr = 0
        #for reg in max2769_defs.MAX2769_Default_Regs:
        for reg in max2769_defs.MAX2769_Default_AMK_4MS:
    
            regNow = reg 
            self.gps_write_spi(addr,regNow)
            #print(addr,hex(reg))    
            addr += 1
        
        print("GPS chip is configured for IF=4.0960MHz @ 16.368MSPS")
    
    def gps_0IF_config(self):
        self.gps_write_spi(max2769_defs.MAX2769_CONF1, max2769_defs.CONF1)
        self.gps_write_spi(max2769_defs.MAX2769_CONF2, max2769_defs.CONF2)
        self.gps_write_spi(max2769_defs.MAX2769_CONF3, max2769_defs.CONF3)
        self.gps_write_spi(max2769_defs.MAX2769_PLLCONF, max2769_defs.PLLCONF)
        self.gps_write_spi(max2769_defs.MAX2769_PLLIDR, max2769_defs.PLLIDR)
        self.gps_write_spi(max2769_defs.MAX2769_CFDR, max2769_defs.CFDR)
        print("GPS chip is configured for IF=0MHz @ 4.096MSPS")
