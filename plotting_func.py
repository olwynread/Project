#This module contains functions to facilitate the plotting of bandstructures from Materials Project, 2DMatpedia, 
#and Aflow to then be assesed for flat bands.

import matplotlib.pyplot as plt

def pretty_plot(width, height=2.4, dpi=None):

    """
    This is a stripped down version of Pymatgen's 'pretty_plot' function, provides a plot in a standard style
    with user choice of dimensions and dpi.

    Args:
        width (float): Width of plot in inches.
        height (float): Height of plot in inches.
            ratio.
        dpi (int): Sets dot per inch for figure. Defaults to 300.

    Returns:
        Matplotlib plot object.
    """

    plt.figure(figsize=(width, height), facecolor="w", dpi=dpi)
    ax = plt.gca()

    ax.spines['top'].set_visible(False) 
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    return plt

def plotting_function(distances, energies, width, lw, Aflow = False):

    """
    Adds the distance and energy data to a 'pretty_plot' matplotlib object

    Args:
        distances (list): List of arrays containing data to be plotted along the abscissa
        energies (list): List of arrays containg data to be plotted along the ordinate
        width (float): Width of plot in inches, corresponding to the number of k-point gaps
        lw (float): Sets line width for the image
        Aflow (bool): If the data is from Aflow the energy arrays are already transposed

    Returns:
        Matplotlib plot object with with data added.
    """
    plot = pretty_plot(width, 2.4, dpi= 50)
    if Aflow:
        for dist, ene in zip(distances, energies):
            plot.plot(dist, ene, c='#000000', lw = lw, ls='-')
    else:
        for dist, ene in zip(distances, energies):
            plot.plot(dist, ene.T, c='#000000', lw = lw, ls='-')
    plot.ylim([-1,1])
    plot.grid(False)
    plot.axis(False)
    plot.xlabel(" ")
    plot.ylabel(" ")
    plot.tick_params(axis='y', length=0, labelsize=0)
    plot.tick_params(axis='x', length=0, labelsize=0)
    plot.margins(0,0)
    plot.subplots_adjust(left=0, right=1.0, top=1.0, bottom=0.0)
    return plot
