import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import seaborn as sns; sns.set()

df = pd.read_csv('xyz.log', header=None)

sns.distplot(df[[2]])

mu = 0.
#sigma = 0.0612143
#sigma = 0.06822887
sigma = 0.04287651
x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
plt.plot(x, mlab.normpdf(x, mu, sigma))

plt.show()

