"""
This module provides a `pyserial` interface to instruments called FastDACs that live in the Quantum Devices Group at UBC, Vancouver. The original author is Ruiheng Su. 
"""

import serial
import struct
import numpy as np
from pathlib import Path


class FastDAC():

    def __init__(self, port: str, baudrate: int, timeout: int, testing=False, verbose=False, datapath="Measurement_Data"):
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
        self.verbose = verbose
        # private class variables
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__port = port
        if not testing:
            try:
                """
                some times the port is already occupied, and will throw an exception
                if the port is not connected anywhere else, restarting the terminal,
                or the jupyter session will help.
                """
                self.ser = serial.Serial(port, baudrate, timeout=timeout)
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.ser.read_all()
                id = self.IDN()
                assert id, "Empty IDN Received."
                print(id)
            except Exception as e:
                try:
                    self.ser.close()
                except:
                    pass
                print(e)
                # raise
        else:
            self.ser = None

        self.__datapath = datapath
        Path(datapath).mkdir(parents=True, exist_ok=True)

    @property
    def datapath(self):
        return self.__datapath

    @property
    def baudrate(self):
        return self.__baudrate

    @baudrate.setter
    def baudrate(self, br):
        # set the baudrate
        self.__baudrate = br
        # make new Serial port object
        self.ser.baudrate = self.__baudrate
        print("Baudrate MODIFIED")

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, to):
        # set the timeout
        self.__timeout = to
        self.ser.timeout = self.__timeout
        print("Timeout MODIFIED")

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, po):
        # set the baudrate
        self.__port = po
        # make new Serial port object
        self.ser.port = self.__port
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
        if self.verbose:
            print("CMD: {}".format(command))

        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(command)

        try:
            data = self.ser.readline()
            if self.verbose:
                print(data)
            data = data.decode('ascii').rstrip('\r\n')
        except:
            self.ser.close()
            raise
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
        if self.verbose:
            print("CMD: {}".format(command))
        if not self.ser.is_open:
            self.ser.open()
        self.ser.write(command)
        if close:
            self.ser.close()

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

        if self.verbose:
            print(cmd)
        if not self.ser.is_open:
            self.ser.open()

        self.ser.write(bytes(cmd, "ascii"))

        channel_readings = {ac: np.zeros(steps) for ac in channels}
        try:
            for i in range(0, steps):
                for channel in channels:
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

        if self.verbose:
            print(cmd)
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

        "The sum of the conversion times of all selected channels will determine overall sample rate.  Shorter conversion times result in more measured noise; Refer to the AD7734 datasheet for typical noise vs conversion times (chopping is always enabled). For the AD7734, conversion times faster than approximately 300µs will start to exhibit a linear calibration offset >1mV at full range. If desired, this offset can be calibrated out using the provided calibration functions. Maximum conversion time: 2686µs. Minimum conversion time: 82µs. The function will return the actual closest possible setting."

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
        """Returns the convert time on the specified channel

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

    def check_conversion_time(self, channels=[0, 1, 2, 3], reps=100):
        """Checks conversion time on every channel, for the specified reps

        Parameters
        ----------
        channels : list, optional 
            List of ADC channels to check conversion time for 

        Returns
        -------
        A list containing the read conversion times as integers
        """

        read = list()
        for i in range(0, reps):
            for ac in channels:
                time_read = int(self.READ_CONVERT_TIME(ac))
                if time_read not in read:
                    read.append(time_read)

        return read
