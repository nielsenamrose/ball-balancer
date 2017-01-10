# -*- coding: utf-8 -*-
"""
Created on Sun Jan 08 16:40:09 2017

@author: Christian
"""

import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt('d:/temp/servo.csv', delimiter=' ', names=['t', 'v', 'a'])

plt.plot(data["t"], data["a"], c='r', label='the data')
plt.show()