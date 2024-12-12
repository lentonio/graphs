# -*- coding: utf-8 -*-
"""pure_maths_graphs.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1B0w92EBeGwzmySfnQhr20aqzm9tq0al4

# Import and modify packages
"""

import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, latex
import streamlit as st

# Add NumPy-style inverse trig function names to SymPy so they work with both libraries
sp.arcsin = sp.asin
sp.arccos = sp.acos
sp.arctan = sp.atan

# Define Up Learn's colour palette
MY_COLORS = {
    'blue': '#82DCF2',
    'red': '#EF665F',
    'green': '#8FE384',
    'yellow': '#FFC753',
    'orange': '#FF8A56',
    'pink': '#F688C9',
    'grey': '#4C5B64'
}

"""# Set axes, gridlines and image size"""

st.markdown(
    """
    <style>
    .stNumberInput > div > input {
        width: 70px !important;  /* Adjust input box width */
        text-align: center;      /* Center-align text in the box */
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(r" ")
with col2:
    st.markdown(r"Lower bounds")
with col3:
    st.markdown(r"Lower bounds")

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown(r"x")
with col5:
    x_lower = st.number_input("Lower bound for x:", value=-2.0, label_visibility="collapsed")
with col6:
    x_upper = st.number_input("Upper bound for x:", value=8.0, label_visibility="collapsed")

# Y inputs in one row
col7, col8, col9 = st.columns(3)
with col7:
    st.markdown(r"y")
with col8:
    y_lower = st.number_input("Lower bound for y:", value=-2.0, label_visibility="collapsed")
with col9:
    y_upper = st.number_input("Upper bound for y:", value=8.0, label_visibility="collapsed")

# 2.5% padding so axis labels don't hit edge
xdifference = xuserupper - xuserlower
ydifference = yuserupper - yuserlower
xlower = xuserlower - 0.025 * xdifference
xupper = xuserupper + 0.025 * xdifference
ylower = yuserlower - 0.025 * ydifference
yupper = yuserupper + 0.025 * ydifference

# Axis values and ticks
showvalues = True     # Set to False to hide axis values
showticks = False     # Set to False to hide axis ticks

# Axis steps (displays fractions over decimals; for steps of pi use 'np.pi', e.g. 0.5*np.pi for steps of pi/2)
xstep = 2           # x-axis steps
ystep = 2           # y-axis steps

# Grid style
gridstyle = 'minor'  # Set as 'none', 'major', or 'minor'
xminordivisor = 4    # Subdivisor for minor gridlines on x-axis (ignore if gridstyle is 'none' or 'major')
yminordivisor = 4    # Subdivisor for minor gridlines on y-axis (ignore if gridstyle is 'none' or 'major')

# Image size
imageheight = 10     # Height of image in inches
imagewidth = 10      # Width of image in inches

x_init = np.linspace(xlower, xupper, 100000)
y_init = np.zeros_like(x_init)  # Create corresponding y values

"""# Add explicit functions

The variable 'x' is created for you to use in your function definitions.

It spans from xlower to xupper, defined above, with 100000 evenly-spaced points.
"""

x = np.linspace(xlower, xupper, 100000) # If the shape of the graph doesn't look right, try increase the number of points - though 100000 is usually enough!
x_sym = sp.Symbol('x')                  # Creates a symbolic version of x (which you may or may not need)

def y1_func(x, lib):
    y = (x-3)**2                        # Write your function y1 here
    if isinstance(x, np.ndarray):       # Check if we're using numpy
        threshold_change = 10000
        dy = lib.abs(lib.diff(y))
        y[1:][dy > threshold_change] = lib.nan    # Handles asymptotes
        y[:-1][dy > threshold_change] = lib.nan
        y[(y < ylower*100000) | (y > yupper*100000)] = np.nan   # Filter extreme y values out
    return y
y1 = y1_func(x, np)                     # Creates a numeric version of y1 (an array of 100000 y1 values)
y1_sym = y1_func(x_sym, sp)             # Creates a symbolic version of y1 (which you may or may not need)
y1color = MY_COLORS['blue']             # Choose a colour
y1style = '-'                           # Try '-', '--', ':', '-.' for continuous, dashed, dotted, and dash-dotted lines
#                                       Note: using (0, (5, 5)) gives more control over the dash pattern if '--' is not working well: the values are offset, dash length and gap length

"""To add more functions, follow the same pattern.

The code looks for y1 to plot, then y2, and so on until it doesn't find one.
"""

def y3_func(x, lib):
    y = 3 * x                # Write your function y1 here
    if isinstance(x, np.ndarray):       # Check if we're using numpy
        threshold_change = 10000
        dy = lib.abs(lib.diff(y))
        y[1:][dy > threshold_change] = lib.nan    # Handles asymptotes
        y[:-1][dy > threshold_change] = lib.nan
        y[(y < ylower) | (y > yupper)] = np.nan  # Filter y values outside range
    return y
y3 = y3_func(x, np)
y3_sym = y3_func(x_sym, sp)
y3color = MY_COLORS['pink']
y3style = '--'

"""You may want to delete a function without resetting everything.

If you want to replace it with a new function, just change the code and run it again.

But if you *only* delete the function y3, for example, run this code
"""

del y3

"""# Add parametric functions

The variable 't' is automatically created for you to use in your function definitions.

It spans from xlower to xupper, defined above, with 100000 points.

Note: don't skip or duplicate variables y1, y2, etc. between the explicit and implicit functions.
"""

t = np.linspace(-100, 100, 100000)    # If the shape of the graph doesn't look right, try increase the number of points - though 100000 is usually enough!
t_sym = sp.Symbol('t')                # Creates a symbolic version of t (which you might or might not need)

def x2_func(t, lib):
    return 15*lib.cos(t)              # Write your function x2 here
x2 = x2_func(t, np)                   # Creates a numeric version of x2 (an array of 100000 x2 values)
x2_sym = x2_func(t_sym, sp)           # Creates a symbolic version of x2 (which you might or might not need)

def y2_func(t, lib):
    return 0.3*t**2-10                    # Write your function y2 here
y2 = y2_func(t, np)                   # Creates a numeric version of y2 (an array of 100000 y2 values)
y2_sym = y2_func(t_sym, sp)           # Creates a symbolic version of y2 (which you might or might not need)

y2color = 'red'                       # Choose a colour
y2style = (0, (5, 5))                 # Try '-', '--', ':', '-.' for continuous, dashed, dotted, and dash-dotted lines
#                                       Note: using (0, (5, 5)) gives more control over the dash pattern if '--' is not working well: the values are offset, dash length and gap length

"""To add more functions, follow the same pattern.

The code looks for y1 to plot, then y2, and so on until it doesn't find one.
"""

def x4_func(t, lib):
    return 15*lib.log(t)
x4 = x4_func(t, np)
x4_sym = x4_func(t_sym, sp)

def y4_func(t, lib):
    return 2**t+10
y4 = y4_func(t, np)
y4_sym = y4_func(t_sym, sp)

y4color = 'purple'
y4style = '-.'

"""To delete a function y4, for example, run this code"""

del y4

"""# Create the graph"""

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

        if style == 'none':
            ax.grid(False)
        elif style == 'major':
            ax.grid(True, which='major', color='#666666', linestyle='-', alpha=0.5)
        elif style == 'minor':
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

# Create the base graph
fig, ax = create_graph(xlower, xupper, ylower, yupper, xstep, ystep, gridstyle,
                 xminordivisor, yminordivisor, imagewidth, imageheight, skip_static_plots=False)

ax.plot(x_init, y_init, alpha=0)  # Plot invisible points

# Remove unnecessary white space
ax.margins(x=0, y=0)  # Remove margins
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)  # Remove all padding
ax.set_xlim(xlower, xupper)  # Force exact limits
ax.set_ylim(ylower, yupper)  # Force exact limits

"""# Add points, lines and areas

Example 1: plot (1, 4) and (0, 3) with a point and cross, respectively
"""

point1 = ax.plot(1, 4, 'o', color=MY_COLORS['blue'], markersize=6)
point2 = ax.plot(3, 0, 'x', color=MY_COLORS['blue'], markersize=12, markeredgewidth=2)
display(fig)

"""Example 2: show a vertical line at x=3"""

line = ax.axvline(x=3, color=MY_COLORS['red'], linestyle='--', linewidth=2)
display(fig)

"""Example 3: Shade the area between y1 and the x-axis from x = 0 to x = 2."""

area = ax.fill_between(x, y1, 0, where=(x > 0) & (x < 2), color=MY_COLORS['blue'], alpha=0.3)
display(fig)

"""Example 4: shade the area between y1 and y3 from the first intersection point to the second.

Note that this only really works with algebraic functions.
"""

intersection_points = sp.solvers.solve(y1_sym - y3_sym, x_sym)      # Solve y1 = y3 to find intersection points (note: this requires the symbolic version of y1 and y3)
intersection_points = [float(p) for p in intersection_points]       # Convert to float (i.e. a decimal number rather than a symbolic number like pi)
x_lower = intersection_points[0]                                    # Sets the first intersection point as the start of the shaded area
x_upper = intersection_points[1]                                    # Sets the second intersection point as the end of the shaded area
ax.fill_between(x, y1, y3, where=(x >= x_lower) & (x <= x_upper), color=MY_COLORS['green'], alpha=0.3)
display(fig)

"""Example 5: show n trapezia between lower and upper limits."""

n = 5                                                               # Number of trapezia
lowertrap = -10                                                     # Lower limit of shaded area
uppertrap = 10                                                      # Upper limit of shaded area
x_trap = np.linspace(lowertrap, uppertrap, n + 1)                   # Divide the range into n intervals
y_trap = y1_func(x_trap, np)                                        # Compute y1 at the trapezium boundaries
for i in range(n):                                                  # Plot the trapezia
    x_vertices = [x_trap[i], x_trap[i], x_trap[i + 1], x_trap[i + 1]]
    y_vertices = [0, y_trap[i], y_trap[i + 1], 0]
    ax.fill(x_vertices, y_vertices, color=MY_COLORS['orange'], edgecolor=MY_COLORS['orange'], alpha=0.5)
display(fig)

"""**To clear all, rerun 'Create the graph'**

# Create animated graph

Define a function as we did before, but include one or more parameters that will change.

This time, we don't actually create the function immediately.

We'll do that repeatedly for each frame once we animate.
"""

preview_mode = True # Toggle between preview and final render quality

n_points = 1000 if preview_mode else 100000
x_anim = np.linspace(xlower, xupper, n_points)
x_sym = sp.Symbol('x')

# Function parameters
a_min = 0.1        # Minimum value for coefficient a
a_max = 5         # Maximum value for coefficient a

def y1_anim(x, a, lib):
    y = a*(x - 4)**2
    if isinstance(x, np.ndarray):
        threshold_change = 10000
        dy = lib.abs(lib.diff(y))
        y[1:][dy > threshold_change] = lib.nan
        y[:-1][dy > threshold_change] = lib.nan
        y[(y < ylower*100000) | (y > yupper*100000)] = np.nan
    return y

"""Then run this cell to create the animation:"""

# Animation parameters
frames = 72         # Number of frames (1 second at 24fps)
interval = 125/3    # Time between frames (milliseconds) - approximately 41.67ms for 24fps
preview_mode = True # Toggle between preview and final render quality

def update(frame):
    for line in ax_anim.lines[1:]:
        line.remove()
    t = frame/frames
    a = a_min + t * (a_max - a_min)
    y = y1_anim(x_anim, a, np)  # Numeric version for plotting
    line = ax_anim.plot(x_anim, y, color=MY_COLORS['blue'], linewidth=2)

    # If you need symbolic version at any point:
    # y_sym = y1_anim(x_sym, a, sp)
    return ax_anim.get_lines()

# Create figure and axis for animation
fig_anim, ax_anim = create_graph(xlower, xupper, ylower, yupper, xstep, ystep,
                                gridstyle, xminordivisor, yminordivisor,
                                imagewidth, imageheight, skip_static_plots=True)

ax_anim.margins(x=0, y=0)
fig_anim.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
ax_anim.set_xlim(xlower, xupper)
ax_anim.set_ylim(ylower, yupper)

plt.close(fig_anim)

# Initialize the line
line, = ax_anim.plot([], [], color=MY_COLORS['blue'], linewidth=2)

# Create the animation
anim = FuncAnimation(fig_anim, update, frames=frames,
                    interval=interval, blit=True)

HTML(anim.to_jshtml())

"""# Save the graph to GDrive

Save a static image with this code.

Type in your chosen file path.

You can also change the file name and file type (to svg, for example).
"""

output_path = '/content/drive/MyDrive/Colab Notebooks/Figures/figure1.png' # Set filepath here

fig.tight_layout(pad=0)
fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)
print(f"File saved to: {output_path}")

"""Save an animation with this code.

Again, you can also change the file path, file name and file type (to mp4, for example).
"""

output_path = '/content/drive/MyDrive/Colab Notebooks/Figures/animated_figure1.gif'  # Set filepath here

fig_anim.tight_layout(pad=0)
anim.save(output_path, writer='pillow')
print(f"Animation saved to: {output_path}")

"""# Function reference

Here are examples of functions you can use:

**Basic Operations**:

*   x + 5          : addition
*   x - 5          : subtraction
*   x * 5          : multiplication (note: must be used for all coefficients, e.g. 2*x rather than 2x)
*   x / 5          : division
*   x**5           : exponentiation


**Trigonometric Functions:**

*   lib.sin(x)     : sine of x
*   lib.cos(x)     : cosine of x
*   lib.tan(x)     : tangent of x
*   lib.cot(x)     : cotangent of x
*   lib.sec(x)     : secant of x
*   lib.csc(x)     : cosecant of x
*   lib.arcsin(x)  : inverse sine
*   lib.arccos(x)  : inverse cosine
*   lib.arctan(x)  : inverse tangent


**Exponential and Logarithmic Functions:**

*   lib.exp(x)     : e^x
*   2**x           : 2^x
*   lib.log(x)     : natural logarithm (ln)
*   lib.log(x, 10) : logarithm base 10
*   lib.log(x, 2)  : logarithm base 2


**Other Functions:**

*   lib.root(x, 2) : square root
*   lib.root(x, 3) : cube root
*   lib.abs(x)     : modulus
"""
