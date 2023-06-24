import matplotlib.pyplot as plt
import numpy as np

import torch

from teng_ml.util import model_io as mio
from teng_ml.util.settings import MLSettings
from teng_ml.util.split import DataSplitter

from m_teng.backends.keithley import keithley

def _update_print(i, ival, vval):
    print(f"n = {i:5d}, I = {ival: .12f} A, U = {vval: .5f} V" + " "*10, end='\r')

class _Monitor:
    """
    Monitor v and i data
    """
    def __init__(self, max_points_shown=None, use_print=False):
        self.max_points_shown = max_points_shown
        self.use_print = use_print
        self.index = []
        self.vdata = []
        self.idata = []

        plt.ion()
        self.fig1, (self.vax, self.iax) = plt.subplots(2, 1, figsize=(8, 5))

        self.vline, = self.vax.plot(self.index, self.vdata, color="g")
        self.vax.set_ylabel("Voltage [V]")
        self.vax.grid(True)

        self.iline, = self.iax.plot(self.index, self.idata, color="m")
        self.iax.set_ylabel("Current [A]")
        self.iax.grid(True)

    def update(self, i, ival, vval):
        if self.use_print:
            _update_print(i, ival, vval)
        self.index.append(i)
        self.idata.append(ival)
        self.vdata.append(vval)
        # update data
        self.iline.set_xdata(self.index)
        self.iline.set_ydata(self.idata)
        self.vline.set_xdata(self.index)
        self.vline.set_ydata(self.vdata)
        # recalculate limits and set them for the view
        self.iax.relim()
        self.vax.relim()
        if self.max_points_shown and i > self.max_points_shown:
            self.iax.set_xlim(i - self.max_points_shown, i)
            self.vax.set_xlim(i - self.max_points_shown, i)
        self.iax.autoscale_view()
        self.vax.autoscale_view()
        # update plot
        self.fig1.canvas.draw()
        self.fig1.canvas.flush_events()

    def __del__(self):
        plt.close(self.fig1)


class _ModelPredict:
    colors = ["red", "green", "purple", "blue", "orange", "grey", "cyan"]
    def __init__(self, instr, model_dir):
        """
        @param model_dir: directory where model.plk and settings.pkl are stored

        Predict the values that are currently being recorded
        @details:
            Load the model and model settings from model dir
            Wait until the number of recoreded points is >= the size of the models DataSplitter
            Collect the data from the keithley, apply the transforms and predict the label with the model
            Shows the prediction with a bar plot
        """
        self.instr = instr
        self.model = mio.load_model(model_dir)
        self.model_settings: MLSettings = mio.load_settings(model_dir)
        if type(self.model_settings.splitter) == DataSplitter:
            self.data_length = self.model_settings.splitter.split_size
        else:
            self.data_length = 200

        plt.ion()
        self.fig1, (self.ax) = plt.subplots(1, 1, figsize=(8, 5))

        self.bar_cont = self.ax.bar(self.model_settings.labels.get_labels(), [ 1 for _ in range(len(self.model_settings.labels))])
        self.ax.set_ylabel("Prediction")
        self.ax.grid(True)

    def update(self, i, ival, vval):
        buffer_size = keithley.get_buffer_size(self.instr, buffer_nr=1)
        if buffer_size <= self.data_length:
            print(f"ModelPredict.update: buffer_size={buffer_size} < {self.data_length}")
            return
        else:
            ibuffer = keithley.collect_buffer_range(self.instr, (buffer_size-self.data_length, buffer_size), buffer_nr=1)
            vbuffer = keithley.collect_buffer_range(self.instr, (buffer_size-self.data_length, buffer_size), buffer_nr=2)
        if self.model_settings.num_features == 1:  # model uses only voltage
            data = np.vstack((ibuffer[:,0], ibuffer[:,1], vbuffer[:,1])).T
            # print(f"data.shape:", data.shape)
        else:
            raise NotImplementedError(f"Cant handle models with num_features != 1 yet")
        for t in self.model_settings.transforms:
            data = t(data)
        data = np.reshape(data[:,2], (1, -1, 1))  # batch_size, seq, features
        with torch.no_grad():
            x = torch.FloatTensor(data)   # select voltage data, without timestamps
            # print(x.shape)

            prediction = self.model(x)  # (batch_size, label-predictions)
            prediction = torch.nn.functional.softmax(prediction)  # TODO remove when softmax is already applied by model
            predicted = torch.argmax(prediction, dim=1, keepdim=False)  # -> [ label_indices ]
            # print(f"raw={prediction[0]}, predicted_index={predicted[0}")
            label = self.model_settings.labels[predicted[0]]
            # print(f"-> label={label}")

        self.bar_cont.remove()
        self.bar_cont = self.ax.bar(self.model_settings.labels.get_labels(), prediction[0], color=_ModelPredict.colors[:len(self.model_settings.labels)])
        # update plot
        self.fig1.canvas.draw()
        self.fig1.canvas.flush_events()
