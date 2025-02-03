import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, E, latex
from sympy.parsing.latex import parse_latex
import streamlit as st
import io

# Add this constant at the top with the other imports
E = 2.7182818284590452  # Euler's number

def latex_to_python(latex_str, param_var='x'):
    """Converts LaTeX math expression to Python code.
    Returns (python_str, preview_expr) on success or (None, error_msg) on failure.
    param_var: the variable to use in the expression (default 'x' for regular functions, 't' for parametric)"""
    try:
        # Parse LaTeX to SymPy expression
        expr = parse_latex(latex_str)
        
        # Convert to string and replace function names with lib. prefix
        python_str = str(expr)
        st.write(f"Debug - Initial SymPy string: {python_str}")
        
        # Handle the special case of ln(x) first
        if 'log' in python_str and ', E)' in python_str:
            python_str = python_str.replace(f'log({param_var}, E)', f'lib.log({param_var})')
        else:
            # Direct replacements (where latex command = python function name)
            for func in ['sin', 'cos', 'tan', 'exp', 'sqrt']:
                python_str = python_str.replace(func, f'lib.{func}')
            
            # Special cases where latex command ≠ python function name
            replacements = {
                'ln': 'lib.log',  # natural logarithm
                'log(': 'lib.log10(',  # base-10 logarithm (this is the standard in LaTeX)
                'arcsin': 'lib.asin',  # inverse sine
                'arccos': 'lib.acos',  # inverse cosine
                'arctan': 'lib.atan',  # inverse tangent
                'csc': 'reciprocal(sin)',  # cosecant
                'sec': 'reciprocal(cos)',  # secant
                'cot': 'reciprocal(tan)',  # cotangent
            }
            
            for latex_func, py_func in replacements.items():
                python_str = python_str.replace(latex_func, py_func)
        
        st.write(f"Debug - python_str: {python_str}")
        return python_str, expr
    except Exception as e:
        return None, f"Invalid LaTeX: {str(e)}"

def eval_function(user_func, x, lib, ylower=None, yupper=None, param_var='x'):
    """Evaluates the user-defined function with the given library (np or sp).
    For implicit functions, x should be a tuple of (x_sym, y_sym).
    For parametric functions, param_var should be 't'."""
    if isinstance(x, tuple):  # Handle implicit function case
        return eval(user_func, {"x": x[0], "y": x[1], "lib": lib})
    else:  # Handle explicit and parametric function cases
        eval_dict = {
            param_var: x, 
            "lib": lib,
            "log": lib.log,      # Add the actual log function
            "log10": lib.log10,  # Add the actual log10 function
            "E": E
        }
        y = eval(user_func, eval_dict)
        if isinstance(x, np.ndarray) and ylower is not None and yupper is not None:
            threshold_change = 10000
            dy = lib.abs(lib.diff(y))
            y[1:][dy > threshold_change] = lib.nan    # Handles asymptotes
            y[:-1][dy > threshold_change] = lib.nan
            y[(y < ylower) | (y > yupper)] = np.nan  # Filter y values outside range
        return y

def create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
    xminordivisor, yminordivisor, imagewidth, imageheight,
    xuserlower, xuserupper, yuserlower, yuserupper,
    showvalues, axis_weight, label_size, white_background, x=None, skip_static_plots=False):
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
            if white_background:
                label.set_bbox(dict(facecolor='white',
                                  edgecolor='none',  # No edge color
                                  pad=1))            # Padding around the text
            else:
                label.set_bbox(None)  # No background box
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

def get_y_values_for_curve(x_fill, curve_points_x, curve_points_y, take_max=True):
    """
    Get y values for a curve that might have multiple y values per x.
    
    Args:
        x_fill: x values to interpolate at
        curve_points_x: x coordinates of the curve points
        curve_points_y: y coordinates of the curve points
        take_max: if True, take maximum y value for each x, otherwise take minimum
    
    Returns:
        Array of y values corresponding to x_fill points
    """
    # Sort x and y values to ensure proper interpolation
    sort_idx = np.argsort(curve_points_x)
    x_sorted = curve_points_x[sort_idx]
    y_sorted = curve_points_y[sort_idx]
    
    # For each x in x_fill, find the appropriate y value
    y_values = []
    tolerance = 0.01
    
    for x in x_fill:
        # Find all y values for this x (within tolerance)
        matching_y = y_sorted[np.abs(x_sorted - x) < tolerance]
        if len(matching_y) > 0:
            y_values.append(np.max(matching_y) if take_max else np.min(matching_y))
        else:
            y_values.append(np.nan)
    
    return np.array(y_values) 
