import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import seaborn as sns
mpl.rcParams['figure.dpi'] = 300
plt.style.use('seaborn-poster')


def plot_data_dist(main_dir, sort=1):
    '''
    Parameters
    ----------
    main_dir : string/path
        main directory which contains all the classes
    sort : One of [None, 1, 2].
        Whether to sort the data or not.
        __None__: wont sort the data and the dirs will also be shown
        __1__ : sorth by class name
        __2__ : sort by file count
            
    Returns
    -------
    None. just plots the data distribution graph

    '''
    
    file_count = []
    for root, dirs, files in os.walk(main_dir):
        file_count.append((os.path.basename(os.path.normpath(root)), len(files)))
        
    file_count = file_count[1:]
    
    name_classes = np.asarray(file_count)[:,0].astype(str)
    num_class = np.asarray(file_count)[:,1].astype(int)
    
    
    df = pd.DataFrame({'name of class':name_classes, 'file count of class':num_class})
    if sort == 1:
        df = df.sort_values(by=['name of class'])
        # dropping entries with 0 file counts
        df = df[(df[['name of class','file count of class']] != 0).all(axis=1)]
    if sort == 2:
        df = df.sort_values(by=['file count of class'])
        # dropping entries with 0 file counts
        df = df[(df[['name of class','file count of class']] != 0).all(axis=1)]
    
    sns.barplot(x='file count of class', y="name of class", data=df, order=df['name of class'])
    plt.xlabel('Number of Images')

    return df
