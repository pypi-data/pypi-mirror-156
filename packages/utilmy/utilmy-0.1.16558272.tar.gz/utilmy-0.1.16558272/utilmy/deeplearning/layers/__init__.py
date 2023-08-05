import os, pickle, numpy as np
from collections import OrderedDict
from functools import partial
from pathlib import Path
from typing import Optional, Sequence

import torch
from torch import Tensor
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from torch.utils.data import DataLoader







class MultiClassMultiLabel_Head(nn.Module):
    """  Multi Class Multi Label head
    Docs::

        class_label_dict :  {'gender': 2,  'age' : 5}  ##5 n_unique_label

    """
    def __init__(self, layers_dim=[256,64],  class_label_dict=None, dropout=0, activation_custom=None,
                 use_first_head_only= None ):

        super().__init__()
        self.dropout     = nn.Dropout(dropout)
        self.activation  = nn.ReLU() if activation_custom is None else activation_custom
        self.use_first_head_only = use_first_head_only

        if self.use_first_head_only:
            for key,val in class_label_dict.items() :
              break
            self.class_label_dict = {key: val}
        else :
            self.class_label_dict = class_label_dict


        ########Common part #################################################################
        self.linear_list = []
        out_dimi = layers_dim[0]
        for i,dimi in enumerate(layers_dim[1:]) :
            # Layer 1
            in_dimi  = out_dimi
            out_dimi = layers_dim[i]
            self.linear_list.append(nn.Linear(in_features=in_dimi, out_features=out_dimi, bias=False) )

        dim_final = layers_dim[-1]
        self.linear_list.append(nn.Linear(in_features=out_dimi, out_features=dim_final, bias=False))
        self.linear_list = nn.Sequential(*self.linear_list)


        ########Multi-Class ################################################################
        self.head_task_dict = {}
        for classname, n_unique_label in class_label_dict.items():
            self.head_task_dict[classname] = []
            self.head_task_dict[classname].append(nn.Linear(dim_final, n_unique_label))
            if self.use_first_head_only:
               self.head_task_dict[classname].append(nn.Linear(n_unique_label, 1))
            self.head_task_dict[classname] = nn.Sequential( *self.head_task_dict[classname])

        #########Multi-Class ################################################################
        #self.head_task_dict = {}
        #for classname, n_unique_label in class_label_dict.items():
        #    self.head_task_dict[classname] = nn.Linear(dim_final, n_unique_label)


    def forward(self, x):
        for lin_layer in self.linear_list:
           x = self.activation(lin_layer(self.dropout(x)))

        yout = {}
        for class_i in self.class_label_dict.keys():
            yout[class_i] = self.head_task_dict[class_i](x)

            if self.use_first_head_only:
               return yout[ class_i ]


        return yout


    def get_loss(self,ypred, ytrue, loss_calc_custom=None,
                 weights=None, sum_loss=True):
        """ Get losses

        """
        if loss_calc_custom is None :
           loss_calc_fun = nn.CrossEntropyLoss()
        else :
           loss_calc_fun = loss_calc_custom()

        loss_list = []
        for ypred_col, ytrue_col in zip(ypred, ytrue) :
           loss_list.append(loss_calc_fun(ypred[ypred_col], ytrue[ytrue_col]) )

        if sum_loss:
            weights = 1.0 / len(loss_list) * np.ones(len(loss_list))  if weights is None else weights
            lsum = 0.0
            for li,wi in zip(loss_list,weights):
                lsum = lsum + wi * li
            return lsum
        return loss_list

