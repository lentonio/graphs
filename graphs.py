import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, latex
import streamlit as st

sp.arcsin = sp.asin
sp.arccos = sp.acos
sp.arctan = sp.atan

MY_COLORS = {
    'blue': '#82DCF2',
    'red': '#EF665F',
    'green': '#8FE384',
    'yellow': '#FFC753',
    'orange': '#FF8A56',
    'pink': '#F688C9',
    'grey': '#4C5B64'
}

#-------SIDEBAR--------------------

with st.sidebar:
    """# Axes and gridlines"""
    col1, col2, col3 = st.columns(3)
    with col1:
        xuserlowerinput = st.number_input("Lower x:", value=-2.0)
    with col2:
        xuserupperinput = st.number_input("Upper x:", value=8.0)
    with col3:
        x_is_pi = st.segmented_control("x unit", options = ["1", "π"], default = '1', key="unit_control_1")
    xuserlower = xuserlowerinput * (np.pi if x_is_pi == "π" else 1)
    xuserupper = xuserupperinput * (np.pi if x_is_pi == "π" else 1)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        yuserlowerinput = st.number_input("Lower y:", value=-2.0)
    with col5:
        yuserupperinput = st.number_input("Upper y:", value=8.0)
    with col6:
        y_is_pi = st.segmented_control("y unit", options = ["1", "π"], default = '1', key="unit_control_2")
    yuserlower = yuserlowerinput * (np.pi if y_is_pi == "π" else 1)
    yuserupper = yuserupperinput * (np.pi if y_is_pi == "π" else 1)
    
    xdifference = xuserupper - xuserlower
    ydifference = yuserupper - yuserlower
    xlower = xuserlower - 0.025 * xdifference
    xupper = xuserupper + 0.025 * xdifference
    ylower = yuserlower - 0.025 * ydifference
    yupper = yuserupper + 0.025 * ydifference
    
    showvalues = st.checkbox("Show values on axes", value=True)
    showticks = st.checkbox("Show ticks on axes")
    
    if showvalues or showticks:
        col7, col8 = st.columns(2)
        with col7:
            x_base_step = st.number_input("x-axis step:", value=2)
            xstep = x_base_step * (np.pi if x_is_pi == "π" else 1)
        with col8:
            y_base_step = st.number_input("y-axis step:", value=2)
            ystep = y_base_step * (np.pi if y_is_pi == "π" else 1)
    else:
        xstep = 1
        ystep = 1

    gridstyle = st.segmented_control("Gridlines", options = ["None", "Major", "Minor"], default = 'None')

    if gridstyle == 'Minor':
        col9, col10 = st.columns(2)
        with col9:
            xminordivisor = st.number_input("Minor divisor for x:", value=4)
        with col10:
            yminordivisor = st.number_input("Minor divisor for y:", value=4)
    else:
        xminordivisor = 1
        yminordivisor = 1

    if not gridstyle:
        gridstyle = "None"


    """# Image size"""
    col11, col12 = st.columns(2)
    with col11:
        imageheight = st.number_input("Height", value=10)
    with col12:
        imagewidth = st.number_input("Width", value=10)
        

x_init = np.linspace(xlower, xupper, 100000)
y_init = np.zeros_like(x_init)  # Create corresponding y values

#-------------------------------------------------------------------

def create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
                xminordivisor, yminordivisor, imagewidth, imageheight, skip_static_plots=False):
    """Create and save a mathematical graph with the specified parameters."""

    fig, ax = plt.subplots(figsize=(imagewidth, imageheight))

    def plot_function(y, color, style, x_coords=None):
        """Plot a function with specified parameters."""
        if x_coords is None:
            x_coords = x  # Use the default x values for explicit functions (y = f(x))
        ax.plot(x_coords, y,
            color=color,
            linestyle=style,
            linewidth=2) # Vary line width

    def set_grid_style(style):
        """Set the grid style."""
        # Always set major locators
        ax.set_xticks(np.arange(xuserlower, xuserupper + xstep, xstep))
        ax.set_yticks(np.arange(yuserlower, yuserupper + ystep, ystep))

        if style == 'None':
            ax.grid(False)
        elif style == 'Major':
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5)
        elif style == 'Minor':
            ax.xaxis.set_minor_locator(plt.MultipleLocator(xstep/xminordivisor))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(ystep/yminordivisor))
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5)
            ax.grid(True, which='minor', color='#999999', linestyle='-', alpha=0.2)
            ax.tick_params(which='minor', length=0)
        else:
            raise ValueError("Style must be 'none', 'major', or 'minor'")

    def sympy_formatter(x, pos):
        """Format a number as a LaTeX expression."""
        sym_expr = nsimplify(x, [pi])
        latex_str = latex(sym_expr)
        latex_str = latex_str.replace(r'\frac', r'\dfrac')
        return f'${latex_str}$'

    # Plot all functions (unless using this function for animation)
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

    # Set up axes
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(1.5)    # y-axis
    ax.spines['bottom'].set_linewidth(1.5)  # x-axis
    ax.spines['left'].set_color('#435159')
    ax.spines['bottom'].set_color('#435159')

    if showticks:
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
    else:
        ax.yaxis.set_ticks_position('none')
        ax.xaxis.set_ticks_position('none')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Apply grid and formatting
    set_grid_style(gridstyle)

    if showvalues:
        ax.xaxis.set_major_formatter(FuncFormatter(sympy_formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(sympy_formatter))
        ax.tick_params(axis='both', labelsize=12, labelfontfamily='sans-serif', colors = '#435159')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
          label.set_bbox(dict(facecolor='white',
                          edgecolor='none',  # No edge color
                          pad=1))            # Padding around the text
        # Remove zero labels
        yticks = ax.get_yticks()
        xticks = ax.get_xticks()
        ax.set_yticks(yticks[yticks != 0])
        ax.set_xticks(xticks[xticks != 0])
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    ax.set_xlim(xlower, xupper)
    ax.set_ylim(ylower, yupper)

    return fig, ax  # Return the figure and axis objects for further modifications

#-------------------------------------------------------------------

plot_placeholder = st.empty()

fig, ax = create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
                 xminordivisor, yminordivisor, imagewidth, imageheight, skip_static_plots=False)

ax.plot(x_init, y_init, alpha=0)  # Plot invisible points
ax.margins(x=0, y=0)  # Remove margins
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)  # Remove all padding
ax.set_xlim(xlower, xupper)  # Force exact limits
ax.set_ylim(ylower, yupper)  # Force exact limits

#-------------------------------------------------------------------

plot_placeholder.pyplot(fig)

col13, col14 = st.columns([7, 1])
with col13:
    user_input = st.text_input("Enter function", value="0.1 * x**2 * lib.sin(3*x)", label_visibility="collapsed")
with col14:
    if st.button("Plot"):
        x = np.linspace(xlower, xupper, 100000)
        x_sym = sp.Symbol('x') 

        def eval_function(user_func, x, lib):
            """Evaluates the user-defined function with the given library (np or sp)."""
            return eval(user_func, {"x": x, "lib": lib})
        
        y1 = eval_function(user_input, x, np)
        fig, ax = create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
                 xminordivisor, yminordivisor, imagewidth, imageheight, skip_static_plots=False)
        ax.plot(x_init, y_init, alpha=0)  # Plot invisible points
        ax.margins(x=0, y=0)  # Remove margins
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)  # Remove all padding
        ax.set_xlim(xlower, xupper)  # Force exact limits
        ax.set_ylim(ylower, yupper)  # Force exact limits

        plot_placeholder.pyplot(fig)
