"""
Ruiheng Su 
August 9 2021

UBC QDev
"""
import time
import serial
import numpy as np
from threading import Thread, Timer

import queue
import serial

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


def receiving(ser, q, s_to_read):
    logging.debug('Starting')

    start = time.time()
    while (time.time() - start) < s_to_read:
        # Read output from ser
        data = ser.readline()
        output = data.decode('ascii').rstrip('\r\n')
        # Add output to queue
        q.put(output)

    logging.debug('Exiting')


def writing(q, filename, timeout=1):
    logging.debug('Starting')

    start = time.time()
    while True:
        try:
            output = q.get(timeout=timeout)
        except:
            break
        else:
            since = time.time() - start
            with open(filename, "a+") as f:
                f.write(output)
                f.write(",")

    logging.debug('Exiting')


def plotting(q, fig, timeout=1):
    logging.debug('Starting')

    start = time.time()
    scatter = fig.data[0]
    # run while the queue is not empty or timeout has not expired
    while True:
        try:
            output = q.get(timeout=timeout)
        except:
            break
        else:
            since = time.time() - start
            with fig.batch_update():
                scatter.x += tuple([since, ])
                scatter.y += tuple([float(output), ])
    logging.debug('Exiting')


class ThreadedSerial():

    def __init__(self, port, **kwargs):
        try:
            self.ser = serial.Serial(port, **kwargs)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        except serial.serialutil.SerialException:
            # no serial connection
            try:
                self.ser.close()
            except:
                pass

        self.q = queue.Queue()

    @property
    def is_open(self):
        return self.ser.is_open

    @property
    def baudrate(self):
        return self.ser.baudrate

    @baudrate.setter
    def baudrate(self, br):
        # make new Serial port object
        self.ser.baudrate = self.br

    @property
    def timeout(self):
        return self.ser.timeout

    @timeout.setter
    def timeout(self, to):
        self.ser.timeout = to

    @property
    def port(self):
        return self.ser.port

    @port.setter
    def port(self, po):
        self.ser.port = po

    def open(self):
        self.ser.open()

    def write(self, cmd, close=True):
        t = Thread(name='Writer', target=self.__threaded_write, args=(
            cmd, close))
        t.start()
        t.join()
    
    def __threaded_write(self, cmd, close: bool):
        if not self.ser.is_open:
            self.ser.open()
        self.ser.write(cmd)
        if close:
            self.ser.close()

    def read(self, bytes: int):
        t = Thread(name='Reader', target=self.__threaded_read, args=(bytes, ))
        t.start()
        
    def __threaded_write(self, cmd, close: bool):
        if not self.ser.is_open:
            self.ser.open()
        self.ser.write(cmd)
        if close:
            self.ser.close()

    def __threaded_read(self, bytes):
        if not self.ser.is_open:
            self.ser.open()
        data = self.ser.read(bytes)
        # Add output to queue
        self.q.put(data)

    def start_reading(self, s_to_read: float):
        self.reader = Thread(name='Reader', target=receiving, args=(
            self.ser, self.q, s_to_read), daemon=True)
        self.reader.start()

    def read_complete(self,):
        print("DONE")


class SerialReaderWriter(ThreadedSerial):

    def __init__(self, port, **kwargs):
        super().__init__(port, **kwargs)

    def start_writing(self, filename):
        self.writer = Thread(target=writing, args=(
            self.q, filename), daemon=True)
        self.writer.start()


class SerialReaderPlotter(ThreadedSerial):

    def __init__(self, port, **kwargs):
        super().__init__(port, **kwargs)

    def start_plotting(self, figure):
        self.writer = Thread(name='Plotter', target=plotting, args=(
            self.q, figure))
        self.writer.start()


if __name__ == "__main__":
    import plotly.graph_objs as go
    fig = go.FigureWidget(data=[go.Scatter(x=[], y=[])])
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (C)",
    )
    s = SerialReaderPlotter("COM8", baudrate=9600)
    s.start_reading(10)
    s.start_plotting(fig)
