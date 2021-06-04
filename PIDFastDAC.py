"""
This module provides a `pyserial` interface to instruments called FastDACs that live in the Quantum Devices Group at UBC, Vancouver. The original author is Ruiheng Su. 

The `PIDFastDAC` class is a subclass of the `FastDAC` class.
"""
from os import close
import time
import numpy as np
from FastDAC import FastDAC


class PIDFastDAC(FastDAC):

    def __init__(self, port, baudrate, timeout, testing=False, verbose=False):
        super().__init__(port, baudrate, timeout, testing, verbose)
        # stops the PID
        self.STOP_PID()
        self.__kp = 0.1
        self.__ki = 1.0
        self.__kd = 0.0
        self.__setp = 0.0
        self.__limit = [-10000.0, 10000.0]
        self.__dir = 1  # default to a direct process
        # dunno why mark defaulted the slew rate to be so large...
        self.__slew = 10000000.0

        self.__SET_PID_DIR(dir=self.__dir)
        self.__SET_PID_SETP(setp=self.__setp)
        self.__SET_PID_LIMS(limit=self.__limit)
        self.__SET_PID_SLEW(max_slewRate=self.__slew)
        self.__SET_PID_TUNE(kp=self.__kp, ki=self.__ki, kd=self.__kd)

    @property
    def slew(self):
        return self.__slew

    @slew.setter
    def slew(self, new_slew):
        self.__slew = new_slew
        self.__SET_PID_SLEW(max_slewRate=self.__slew)

    @property
    def dir(self):
        return self.__dir

    @dir.setter
    def dir(self, new_dir):
        self.__dir = new_dir
        self.__SET_PID_DIR(dir=self.__dir)

    @property
    def limit(self):
        return self.__limit

    @limit.setter
    def limit(self, new_lim):
        self.__limit = new_lim
        self.__SET_PID_LIMS(limit=self.__limit)

    @property
    def setp(self):
        return self.__setp

    @setp.setter
    def setp(self, new_setp):
        self.__setp = new_setp
        self.__SET_PID_SETP(setp=self.__setp)

    @property
    def kp(self):
        return self.__kp

    @kp.setter
    def kp(self, new_kp):
        self.__kp = new_kp
        self.__SET_PID_TUNE(kp=self.__kp, ki=self.__ki, kd=self.__kd)

    @property
    def ki(self):
        return self.__ki

    @ki.setter
    def ki(self, new_ki):
        self.__ki = new_ki
        self.__SET_PID_TUNE(kp=self.__kp, ki=self.__ki, kd=self.__kd)

    @property
    def kd(self):
        return self.__kd

    @kd.setter
    def kd(self, new_kd):
        self.__kd = new_kd
        self.__SET_PID_TUNE(kp=self.__kp, ki=self.__ki, kd=self.__kd)

    @FastDAC.baudrate.setter
    def baudrate(self, br):
        # stop the PID algorith first
        self.STOP_PID()
        # set the baudrate
        self._FastDAC__baudrate = br
        self.ser.baudrate = self._FastDAC__baudrate
        print("Baudrate MODIFIED")

    @FastDAC.timeout.setter
    def timeout(self, to):
        # stop the PID algorith first
        self.STOP_PID()
        # set the baudrate
        self.__timeout = to
        self.ser.timeout = self._FastDAC__timeout
        print("Timeout MODIFIED")

    @FastDAC.port.setter
    def port(self, po):
        # stop the PID algorith first
        self.STOP_PID()
        # set the port
        self.__port = po
        self.ser.port = self._FastDAC__port
        print("Port MODIFIED")

    def START_PID(self, n=0, stopPID=False):
        """Starts the PID function. 

        If n is zero, then the PID algorithm will be allowed run, but no data points will be read. **For n = 0, the serial port will be left open**
        If n is not zero, then read n input-output pairs returned by the FastDAC. The serial port will close after n data points have been read.

        If stopPID is true, then the PID algorithm will also stop. 

        The binary sync characters are 0xA5, 0x5A

        Parameters
        ----------
        n : int, optional 
            n data points to read 

        stopPID : bool, optional
            Stops the FastDAC PID loop after n data points have been collected if set to True. Otherwise, the PID loop is allowed to run. If n = 0, stopPID has no effect

        Raises
        ------
        Assertion error if n is negative

        Returns
        -------
        A dictionary of the values read
        """

        assert n >= 0, "The number of data points cannot be negative"

        if n == 0:
            # start the loop, then close the serial port
            self.write(b"START_PID\r", close = False)
        elif n > 0:
            # start the loop, dont close the serial port yet
            self.write(b"START_PID\r", close=False)
            in_out = {"in": np.zeros(n), "out": np.zeros(n)}
            try:
                for i in range(0, n):
                    in_val = FastDAC.four_bytes_to_float(
                        self.ser.read(4), bigEndian=False)
                    out_val = FastDAC.four_bytes_to_float(
                        self.ser.read(4), bigEndian=False)
                    self.ser.read(2)

                    in_out["in"][i] = in_val
                    in_out["out"][i] = out_val
            except:
                # stop PID and close the serial port on error
                self.STOP_PID()
                raise
            # sucessful completion, stop the loop if stopPID is true
            if stopPID:
                self.STOP_PID()

            return in_out

    def STOP_PID(self):
        """Stops the PID function. 
        """
        # using write method since the FastDAC returns no confirmation
        return self.write(b"STOP_PID\r", close=True)

    def __SET_PID_TUNE(self, kp=0, ki=0, kd=0):
        """Sets tuning parameters PID parameters

        Parameters
        ----------
        Kp : float, optional
        Ki : float, optional 
        Kd : float, optional 

        """
        cmd = "SET_PID_TUNE,{},{},{}\r".format(kp, ki, kd)
        return self.write(bytes(cmd, "ascii"))

    def __SET_PID_SETP(self, setp=0):
        """Sets the PID set point in mV

        Parameters
        ----------
        setp : float, optional 
            The set point in mV

        """
        cmd = "SET_PID_SETP,{}\r".format(setp)
        return self.write(bytes(cmd, "ascii"))

    def __SET_PID_LIMS(self, limit=[-100, 100]):
        """Sets the DAC output limit in mV

        Parameters
        ----------
        limit : list of float, optional 
            limit[0] is the lower limit, limit[1] is the upper limit. The limit can be asymmetric about 0.
        """
        cmd = "SET_PID_LIMS,{},{}\r".format(limit[0], limit[1])
        return self.write(bytes(cmd, "ascii"))

    def __SET_PID_DIR(self, dir=1):
        """Sets the ``direction" of PID control.

        The process variable of a direct process increases with increasing controller output. The process variable of a reverse process decreases with increasing controller output.

        Parameters
        ----------
        dir : 0 or 1, optional 
            dir = 0 represets a reverse process. dir = 1 represents a direct process. 
        """
        cmd = "SET_PID_DIR,{}\r".format(dir)
        return self.write(bytes(cmd, "ascii"))

    def __SET_PID_SLEW(self, max_slewRate=10000000.0):
        """Sets the maximum rate (called the slewRate just to confuse you) to ramp controller output in mV/S

        **Mark decided to default slew rate to a very large number. He wrote: make it big because it intereferes with the pid**

        Parameters
        ----------
        max_slewRate : float, optional
        """
        cmd = "SET_PID_SLEW,{}\r".format(max_slewRate)
        return self.write(bytes(cmd, "ascii"))

    def setp_test(self, settle_time=10, setps=[0, 1000, 2000, 3000], steps=[1000, 2000, 2000, 2000], clip_to_limit=False):
        """ Automatically change the controller setpoint, and run the PID algoritm, and read the results. After reading all the data required, stops the PID.

        Parameters
        ----------
        settle_time : int, optional 
            The number of seconds given for the instrument to settle to `setps[0]`

        setps : list, optional 
            Set Point values in mV to change 

        steps : list, optional 
            The number of samples to take from the Arduino before stopping the PID algorithm 

        clip_to_limit : bool, optional 
            If set the True, then any sample that are larger than the FastDAC limits will be set to the value of the previous sample. This helps to eliminate noise that appears with more aggressive PID parameters

        Returns 
        -------
        Two dictionaries. The first contains key value pairs of process variable and controller output readings. The second contains the values of the argument to this function. This dictionary can be saved, and recovered to run the identitical tests. 
        """

        settings = dict()
        settings.update(locals())

        self.setp = setps[0]  # change set point
        self.START_PID(0)  # start the PID
        time.sleep(settle_time)  # wait for PID to settle
        self.STOP_PID()
        all_readings = list()
        for i, setp in enumerate(setps):
            self.setp = setp
            all_readings.append(self.START_PID(steps[i]))

        self.STOP_PID()
        concat_reading = dict()
        concat_reading["Process Variable"] = np.concatenate([
            r["in"] for r in all_readings])
        concat_reading["Controller Output"] = np.concatenate([
            r["out"] for r in all_readings])
        concat_reading["Set Point"] = np.concatenate([
            np.array([setps[i], ]*steps[i]) for i in range(len(setps))])

        if clip_to_limit:
            for k in concat_reading.keys():
                for i in range(len(concat_reading[k])):
                    if np.abs(concat_reading[k][i]) > np.abs(self.limit[1]) or np.abs(concat_reading[k][i]) > np.abs(self.limit[0]) and i - 1 >= 0:
                        concat_reading[k][i] = concat_reading[k][i-1]

        del settings['self']
        del settings['settings']

        return concat_reading, settings
