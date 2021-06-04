"""
Author: Ruiheng Su

Engineering Physics, UBC

ruihengsu@alumni.ubc.ca

2020
"""

from logging import shutdown
import os
import shutil
import pickle

import numpy as np
from pathlib import Path
import scipy.signal as ss

import MakePlots as MP

SETTING = "settings"
DAT_NAME = "PID"
SETP = "Set Point"
CO = "Controller Output"
PV = "Process Variable"

class Tracker():

    def __init__(self, filename):
        self.name = filename
        self._version = {0: filename}

    def get_version(self, num):
        """
        """
        most_recent = max(self._version.keys())
        if num >= most_recent or num == -1:
            return self._version[most_recent]

        return self._version[num]

    def track(self, name):
        most_recent = max(self._version.keys())
        self._version[most_recent+1] = name


class DataManager():

    def __init__(self, data_path):
        """
        Initializes or loads a given data path
        """
        self.data_path = data_path
        self.__new_run = None
        
        # check if the specified directory is found
        if not os.path.exists(data_path):
            print("{} not found in {}".format(data_path, os.getcwd()))
            raise FileNotFoundError

    def all_runs(self):
        """
        Returns a list of all available profiles/runs in self.data_path
        """
        return os.listdir(self.data_path)

    @property
    def new_run(self):
        return self.__new_run

    @new_run.setter
    def new_run(self, new_run):
        """
        """
        self.__new_run = new_run
        self.init_folder_structure()

    def init_folder_structure(self):
        """
        """
        self.__data = {
            "PID": list(),
            SETTING: list()
        }
        self.paths = dict()
        new_run_path = os.path.join(self.data_path, self.__new_run) 
        for item in sorted(os.listdir(new_run_path)):
            item_path = os.path.join(new_run_path, item)
            if os.path.isdir(item_path):
                self.paths[item] = os.path.join(
                    self.data_path, self.__new_run, item)
                Path(os.path.join(item_path, ".temp")).mkdir(parents=True, exist_ok=True)
        self.load_settings()
        self.load_measurements()

    def load_settings(self):
        for k in self.paths.keys():
            setting_dir = self.paths[k]
            temp_path = os.path.join(setting_dir, ".temp")
           
            files = os.listdir(setting_dir)         
            for i in files:
                if SETTING in i:
                    try:
                        file_path = os.path.join(setting_dir, i)
                        with open(file_path, "rb") as set:
                            setting = pickle.load(set)
                        
                        temp_file_path = os.path.join(
                            temp_path, k + "_"+ Path(i).stem + ".npy")
                        
                        np.save(temp_file_path, setting)
                        self.__data["settings"].append(Tracker(temp_file_path))

                    except:
                        raise

    def load_measurements(self):
        for k in self.paths.keys():
            dat_dir = self.paths[k]
            
            temp_path = os.path.join(dat_dir, ".temp")
           
            files = os.listdir(dat_dir)    
            for i in files:
                if DAT_NAME in i:
                    try:
                        file_path = os.path.join(dat_dir, i)
                        with open(file_path, "rb") as set:
                            dat = pickle.load(set)
                        
                        dat_path = os.path.join(
                            temp_path, k + ".npy")
                        np.save(dat_path, np.column_stack((dat[SETP], dat[PV], dat[CO])))
                        self.__data["PID"].append(Tracker(dat_path))
                    except:
                        raise

    def from_cache(self, filename, version):
        for key in self.__data.keys():
            for trackerObj in self.__data[key]:
                # print(Path(trackerObj.name).stem)
                if filename in Path(trackerObj.name).stem:
                    return trackerObj.get_version(version)
        return None

    def load(self, filename):
        return np.load(filename, allow_pickle=True)

    def list_parsed_data(self):
        """
        """
        parsed_setting = [
            Path(t.name).stem for t in self.__data[SETTING]
        ]
        parsed_dat = [
            Path(t.name).stem for t in self.__data["PID"]
        ]
        return {SETTING: parsed_setting,
                "PID": parsed_dat}

    def plot_curve(self, filename, fig, column, keep=1.0, smoothing_window=1,
                   peak_height=None, peak_samples=None, peak_num=None, peak_offset=None):
        """ Returns a graph object

        Keyword arguments:

        keep -- the fraction of data points to plot

        smoothing_window -- the size of the smoothing window.
        """
        path = self.from_cache(filename, -1)
        data = self.load(path)
        
        label = {0: SETP, 1: PV, 2: CO}
        fig, num_peaks = MP.add_to_figure(
            data[:, column],
            name=label[column],
            fig=fig,
            keep=keep,
            smoothing=smoothing_window,
            peak_height=peak_height,
            peak_samples=peak_samples,
            peak_num=peak_num,
            peak_offset=peak_offset,
        )

        return fig, num_peaks

    def get_trace_num(self, filename):
        """ Returns a graph object
        """
        path = self.from_cache(filename, -1)
        data = self.load(path)
        numcols = data.shape[1]
        return numcols

    def load_summary(self, filename):
        """ Returns a graph object

        Keyword arguments:

        tbox -- integer representing the tunebox number
        """
        path = self.from_cache(filename, -1)
        data = self.load(path)
        return data

    def del_data(self, filename):
        try:
            shutil.rmtree(self.paths[filename])
            self.init_folder_structure()
        except:
            raise

if __name__ == "__main__":

    dm = DataManager("Measurement_Data")
    dm.new_run = "20210526"
    print(dm.paths)
