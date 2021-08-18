"""
This module provides a `pyserial` interface to instruments called FastDACs that live in the Quantum Devices Group at UBC, Vancouver. The original author is Ruiheng Su. 
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
import serial
import struct
from re import I
import numpy as np
from pathlib import Path
from logging import exception

class FastDAC():
    def __init__(self, serialReader, datapath="Measurement_Data"):
        """ Makes a new FastDac object. 

        Parameters
        ----------
        port : str 
            Example "COM5", "dev/ttyacm0"

        baudrate : int 
            Common values are 1750000

        timeout : int 
            How long to wait before giving up trying to connnect to this device 

        testing : bool, optional
            Whether we are testing this class. Will not connect to a device when set to True.

        Returns
        -------
        A str 
        """
        self.ser = serialReader
        
        id = self.IDN()
        assert id, "Empty IDN Received."
        print(id)
        
        self.__datapath = datapath
        Path(datapath).mkdir(parents=True, exist_ok=True)

    @property
    def datapath(self):
        return self.__datapath

    @property
    def baudrate(self):
        return self.ser.baudrate

    @baudrate.setter
    def baudrate(self, br):
        self.ser.baudrate = br

    @property
    def timeout(self):
        return self.ser.timeout

    @timeout.setter
    def timeout(self, to):
        self.ser.timeout = to
        print("Timeout MODIFIED")

    @property
    def port(self):
        return self.ser.timeout.port

    @port.setter
    def port(self, po):
        self.ser.port = po 
        print("Port MODIFIED")

    def query(self, command):
        """Queries a command from the instrument 

        Parameters
        ----------
        command : byte str 
            a ''wellformed" byte string with carriage return at the end  

        Returns
        -------
        A string/byte string  
        """
        
        assert self.ser.q.empty() 
        
        self.ser.write(command)
        self.ser.read(command)
        
        try:
            data = self.ser.q.get(timeout=self.ser.timeout)
            data = data.decode('ascii').rstrip('\r\n')

        except Exception as e: 
            print("No data read from queue.")
            raise e
                  
        self.ser.close()
        return data
        
        
    def write(self, command, close=True):
        """Write a command to the instrument. 

        Parameters
        ----------
        command : byte str 
            a ''wellformed" byte string with carriage return at the end  

        close : bool, optional
            closes the serial port if True. Otherwise, leave the serial port open.
        """
        if not self.ser.is_open:
            self.ser.open()
        self.ser.write(command, close)
        
    @staticmethod
    def two_bytes_to_int(two_bytes, bigEndian=True):
        """Converts a byte string of two bytes to a single integer

        **Now implemented using the struct module.**

        "<<" is the right shift operator; "|" is the bitwise OR operator. We made this a static method so it is not tied to any objects of the class.

        Parameters 
        ----------
        two_bytes : byte
            A byte string of two bytes 

        bigEndian : bool, optional
            whether to unpack using big or little endian

        Returns
        -------
        An integer between 0 to 2^(16)
        """
        if bigEndian:
            # struct unpack returns a tuple
            # ">" represents big endian
            # "H" represents to unpack into an unsigned short
            # alternatively we can just do it manually
            # return int(two_bytes[0] << 8 | two_bytes[1])
            return struct.unpack(">H", two_bytes)[0]
        else:
            return struct.unpack("<H", two_bytes)[0]

    @staticmethod
    def four_bytes_to_float(four_bytes, bigEndian=True):
        """Converts a byte string of four bytes to a single floating point number.

        **Implemented using the struct module**

        Parameters 
        ----------
        four_bytes : byte str
            A byte string of four bytes 

        bigEndian : bool, optional
            whether to unpack using big or little endian

        Returns
        -------
        A signed floating point number
        """

        if bigEndian:
            # struct unpack returns a tuple
            # ">" represents big endian
            # "H" represents to unpack into an unsigned short
            # alternatively we can just do it manually
            # return int(four_bytes[0] << 8*3 | four_bytes[1] << 8*2 | four_bytes[2] << 8 | four_bytes[3])
            return struct.unpack(">f", four_bytes)[0]
        else:
            return struct.unpack("<f", four_bytes)[0]

    @staticmethod
    def map_int16_to_mV(int_val):
        """Maps an integer between 0 to 2^(16) to +/- 10000

        (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

        Parameters 
        ----------
        int_val: int

        Returns
        -------
        An double  
        """
        return (int_val - 0) * (20000.0) / (65536.0) - 10000.0

    def STOP(self):
        """Stops any sweeps or reads that the FastDAC is currently doing
        """
        return self.ser.write(b"STOP\r")

    def NOP(self):
        """The most useful command. Does absolutely nothing. 

        Returns
        -------
        A str 
        """
        return self.query(b"NOP\r")

    def IDN(self):
        """Confirms the identity of the instrument 

        Returns
        -------
        A string, for example:'DAC-ADC_AD7734-AD5764_UNIT5_PIDTEST'
        """
        return self.query(b"*IDN?\r")

    def RDY(self):
        return self.query(b"*RDY?\r")

    def RESET(self):
        """Resets the ADCs, and sets the range to default +/-10 V
        """
        return self.query(b"RESET\r")

    def GET_DAC(self, channel=0):
        """Reads the current DAC output in millivolts

        A DAC output can be thought of as the output of a variable voltage source. 

        Parameters
        ----------
        channel : int, optional 
            The DAC channel to read

        Returns
        -------
        DAC reading : str
            The DAC reading you are looking for     
        """
        cmd = "GET_DAC,{}\r".format(channel)
        return self.query(bytes(cmd, "ascii"))

    def GET_ADC(self, channel=0):
        """Reads the current DAC output in mV

        An ADC input can be thought of as the reading of a voltmeter

        Parameters
        ----------
        channel : int, optional 
            The ADC channel to read

        Returns 
        -------
        ADC reading : str 
            The ADC reading you are looking for

        "NOP" : str
            Something is wrong 
        """
        cmd = "GET_ADC,{}\r".format(channel)
        return self.query(bytes(cmd, "ascii"))

    def SPEC_ANA(self, channels=[0, ], steps=10):
        """Reads a number of points equal to ``steps" from each ADC channels as specified in channels in mV.

        Parameters
        ----------
        channels : list, optional 
            The ADC channels to read

        steps : int, optional
            The number of data points to read 

        Returns 
        -------
        A dictionary where the keys represents the adc channels that was read, and the value is a numpy array of readings. 
        """
        cmd = "SPEC_ANA,{},{}\r".format(
            "".join(str(ac) for ac in channels), steps)

        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(bytes(cmd, "ascii"))

        channel_readings = {ac: list() for ac in channels}
        try:
            while self.ser.in_waiting > 15 or len(channel_readings[0]) < steps:
                for channel in channels:
                    buffer = ""
                    if self.ser.in_waiting > 35:
                        buffer = self.ser.read(20)
                    else:
                        buffer = self.ser.read(2)
                    # separate the buffer
                    info = [buffer[i:i+2] for i in range(0, len(buffer), 2)]
                    for two_b in info:
                        int_val = FastDAC.two_bytes_to_int(two_b)
                        voltage_reading = FastDAC.map_int16_to_mV(int_val)
                        channel_readings[channel].append(voltage_reading)
        except:
            self.ser.close()
            raise
        # .decode('ascii').rstrip('\r\n')
        data = self.ser.readline()
        self.ser.close()
        print(data)

        # convert to numpy array
        for k in channel_readings.keys():
            channel_readings[k] = np.array(channel_readings[k])

        return channel_readings

    def RAMP_SMART(self, channel=0, setPoint=0, rampRate=1000):
        """Changes the output of a DAC channel to the setPoint from its initial value at the rampRate [mV/s].

        Ramps one DAC channel in mV to a specified setPoint at a given ramp rate in 1ms steps. It looks up the current DAC value internally to make sure there are no sudden jumps in voltage. Internally it calls RAMP1 to do the actual ramp. 

        THe FastDAC handles 16 bit numbers. So between +/- 10 V, it is precise to within 1000*(20/2^(16)) mV.

        Parameters
        ----------
        channel : int, optional 
            The DAC channel to ramp

        setPoint : double, optional 
            The voltage in mV to ramp to. The FastDAC has a precision of ~0.3 mV

        rampRate : str, optional 

        Returns
        -------
        "RAMP_FINISHED" : str
            A sucess

        "NOP" : str
            Something is wrong
        """
        cmd = "RAMP_SMART,{},{},{}\r".format(channel, setPoint, rampRate)

        return self.query(bytes(cmd, "ascii"))

    def RAMP_AND_READ(self, DAC_channels=[0, ], ADC_channels=[0, ],  steps=1000, rampRanges={0: [-100, 100], }):
        """Ramps the specified DAC channels, and read on the specified ADC channels at the same time. 

        Parameters
        ----------
        DAC_channels : list, optional 
            A sorted list of DAC channels to ramp. Typically 0,1,2,3

        ADC_channels : list, optional 
            A sorted list of ADC channels to read. Typically 0,1,2,3,4,5,6,7

        steps : int, optional 
            The number of steps each DAC channel should take to go from an initial to a final value in mV.

        rampRanges : dict, optional 
            A dictionary. The key represents the DAC channel number, the associated value is a list containing the initial ad final values that the DAC channel should ramp. The dictionary should be sorted to match the order that the DAC channels are specified in DAC_channels

        Returns
        -------
        A dictionary where the keys represents the adc channels that was read, and the value is a numpy array of readings. 

        "NOP" : str
            Something is wrong
        """
        cmd = "INT_RAMP,"
        cmd = cmd + "".join(str(dc) for dc in DAC_channels) + ","
        cmd = cmd + "".join(str(ac) for ac in ADC_channels) + ","

        for key in rampRanges.keys():
            cmd = cmd + str(rampRanges[key][0]) + ","
        for key in rampRanges.keys():
            cmd = cmd + str(rampRanges[key][1]) + ","

        cmd = cmd + str(steps) + "\r"

        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(bytes(cmd, "ascii"))

        channel_readings = {ac: np.zeros(steps) for ac in ADC_channels}
        try:
            for i in range(0, steps):
                for channel in ADC_channels:
                    int_val = FastDAC.two_bytes_to_int(self.ser.read(2))
                    voltage_reading = FastDAC.map_int16_to_mV(int_val)
                    channel_readings[channel][i] = voltage_reading
        except:
            self.ser.close()
            raise

        data = self.ser.readline().decode('ascii').rstrip('\r\n')
        self.ser.close()
        print(data)

        return channel_readings

    def SET_CONVERT_TIME(self, channel=0, convertTime=1000):
        """Sets the conversion time in microseconds. This is the time required to digitize the analog signal.  

        "The sum of the conversion times of all selected channels will determine overall sample rate.  Shorter conversion times result in more measured noise; Refer to the AD7734 datasheet for typical noise vs conversion times (chopping is always enabled). For the AD7734, conversion times faster than approximately 300us will start to exhibit a linear calibration offset >1mV at full range. If desired, this offset can be calibrated out using the provided calibration functions. Maximum conversion time: 2686us. Minimum conversion time: 82us. The function will return the actual closest possible setting."

        Parameters
        ----------
        channel : int, optional 
            ADC channel to set the conversion time for 

        convert_time : int, optional
            Conversion time in uS

        Returns
        -------
        An integer representing the closest possible conversion time setting.

        """

        cmd = "CONVERT_TIME,{},{}\r".format(channel, convertTime)
        return self.query(bytes(cmd, "ascii"))

    def READ_CONVERT_TIME(self, channel=0):
        """Returns the convert time on the specified channel in uS

        Parameters
        ----------
        channel : int, optional 
            ADC channel to get the conversion time for 

        Returns
        -------
        An string which can be cast into an integer representing the current conversion time setting.

        """

        cmd = "READ_CONVERT_TIME,{}\r".format(channel)
        return self.query(bytes(cmd, "ascii"))

    def read_vs_time(self, duration: int, channels=[0, ]):
        """Reads the specified channel in chuncks, for a number of seconds as specified in duration.

        Parameters
        ----------
        duration : int
            The number of seconds to read ADC channels specifed for 

        channels : list, optional 
            The ADC channels on the fastDAC to read from 
        """

        assert len(channels) > 0, "What? No ADC channel selected \U0001F923"

        c_time = list()
        for c in channels:
            t_read = int(self.READ_CONVERT_TIME(channel=c))
            if t_read not in c_time:
                c_time.append(t_read)

        assert len(c_time) == 1, "What? Bad conversion time \U0001F923"

        c_freq = 1/(c_time[0]*10**-6)  # in Hz

        measure_freq = c_freq/len(channels)
        steps = int(np.round(measure_freq*duration))
        # print(steps)

        cmd = "SPEC_ANA,{},{}\r".format(
            "".join(str(ac) for ac in channels), steps)

        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(bytes(cmd, "ascii"))
        channel_readings = {ac: list() for ac in channels}

        def handle_close(evt):
            self.STOP()
            data = self.ser.readline()
            self.ser.close()

        fig, ax = plt.subplots(figsize=(10, 4))
        fig.canvas.mpl_connect('close_event', handle_close)
        line, = ax.plot([], [])
        x_array = np.linspace(0, duration, steps)
        # ax.set_xlim(0, duration)

        def data_gen():
            try:
                if not self.ser.is_open:
                    self.ser.open()
                time.sleep(0.1)
                while self.ser.in_waiting > 15 or len(channel_readings[channels[0]]) < steps:
                    print(self.ser.in_waiting)
                    for channel in channels:
                        buffer = ""
                        waiting = self.ser.in_waiting
                        if waiting > 1000 + 15:
                            buffer = self.ser.read(1000)
                        elif self.ser.in_waiting > 200+15:
                            buffer = self.ser.read(200)
                        else:
                            buffer = self.ser.read(2)
                        # separate the buffer
                        info = [buffer[i:i+2]
                                for i in range(0, len(buffer), 2)]
                        # print(len(info))
                        for two_b in info:
                            int_val = FastDAC.two_bytes_to_int(two_b)
                            voltage_reading = FastDAC.map_int16_to_mV(int_val)
                            channel_readings[channel].append(voltage_reading)
                    yield len(channel_readings[channels[0]]), 0
            except Exception as e:
                print(e)
                self.ser.close()
                raise

        def animate(data):
            i, _ = data
            y_data = channel_readings[channels[0]]
            line.set_data(x_array[0:i], y_data)
            ymin = np.min(y_data)
            ymax = np.max(y_data)
            ax.set_ylim(ymin, ymax)
            if i == len(x_array):
                ax.set_xlim(0, x_array[i-1])
            else:
                ax.set_xlim(0, x_array[i])
            ax.set_xlabel("Time [S]")
            ax.set_ylabel("")
            ax.figure.canvas.draw()
            return line,

        ani = animation.FuncAnimation(
            fig, animate, data_gen, interval=0, blit=True, repeat=False)
        plt.show()
        # actual_read = len(channel_readings[channels[0]])
        # fig, ax = plt.subplots(figsize=(10, 4))
        # ax.plot(x_array[:actual_read], channel_readings[channels[0]])
        # ax.autoscale(tight=True)
        # ax.set_xlabel("Time [S]")
        # ax.set_ylabel("")
        # plt.show()


if __name__ == "__main__":
    fd = FastDAC("COM3", baudrate=1750000, timeout=1,)
    # print(fd.SPEC_ANA(steps=1000))
    # fd.read_vs_time(10, channels=[1, ])
    print(fd.SPEC_ANA(channels=[1, ], steps=1000))
