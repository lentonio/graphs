import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, latex
import streamlit as st
import io

def create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
    xminordivisor, yminordivisor, imagewidth, imageheight,
    xuserlower, xuserupper, yuserlower, yuserupper,
    showvalues, axis_weight, label_size, x=None, skip_static_plots=False):
    """Create and save a mathematical graph with the specified parameters."""

    #------define some nested functions---------
                    
    def plot_function(y, color, style, x_coords=None):
        """Plot a function with specified parameters."""
        if x_coords is None:
            x_coords = x  # Use the default x values for explicit functions (y = f(x))
        ax.plot(x_coords, y,
            color=color,
            linestyle=style,
            linewidth=axis_weight*1.3) # Vary line width

    def set_grid_style(style):
        """Set the grid style."""
        # Always set major locators
        ax.set_xticks(np.arange(xuserlower, xuserupper + xstep, xstep))
        ax.set_yticks(np.arange(yuserlower, yuserupper + ystep, ystep))

        if style == 'None':
            ax.grid(False)
        elif style == 'Major':
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5, linewidth=axis_weight*0.7)
        elif style == 'Minor':
            ax.xaxis.set_minor_locator(plt.MultipleLocator(xstep/xminordivisor))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(ystep/yminordivisor))
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5, linewidth=axis_weight*0.7)
            ax.grid(True, which='minor', color='#999999', linestyle='-', alpha=0.2, linewidth=axis_weight*0.7)
            ax.tick_params(which='minor', length=0)

    def sympy_formatter(x, pos):
        """Format a number as a LaTeX expression."""
        sym_expr = nsimplify(x, [pi])
        latex_str = latex(sym_expr)
        latex_str = latex_str.replace(r'\frac', r'\dfrac')
        return f'${latex_str}$'

    #------create the graph---------
                    
    fig, ax = plt.subplots(figsize=(imagewidth, imageheight))

    if not skip_static_plots:
        i = 1
        while True:
            try:
                y = eval(f'y{i}')
                color = eval(f'y{i}color')
                style = eval(f'y{i}style')
                try:
                    x_coords = eval(f'x{i}')
                    plot_function(y, color, style, x_coords)
                except NameError:
                    plot_function(y, color, style)
                i += 1
            except NameError:
                break

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_position('zero')
        ax.spines[spine].set_linewidth(axis_weight)
        ax.spines[spine].set_color('#435159')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
                    
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')

    set_grid_style(gridstyle)

    if showvalues:
        ax.xaxis.set_major_formatter(FuncFormatter(sympy_formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(sympy_formatter))
        ax.tick_params(axis='both', 
                       labelsize=label_size, 
                       labelfontfamily='sans-serif', 
                       colors = '#435159')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
          label.set_bbox(dict(facecolor='white',
                          edgecolor='none',  # No edge color
                          pad=1))            # Padding around the text
        yticks = ax.get_yticks()
        xticks = ax.get_xticks()
        ax.set_yticks(yticks[yticks != 0])
        ax.set_xticks(xticks[xticks != 0])
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    ax.set_xlim(xlower, xupper)
    ax.set_ylim(ylower, yupper)

    return fig, ax 
