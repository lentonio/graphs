import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, latex
import streamlit as st
import io

from graph_utils import create_graph, eval_function, latex_to_python

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

PI = 3.1415927


#-------PAGE CONFIG----------------

st.set_page_config(
    page_title="Graph App",
    layout="wide"  # Enable wide layout
)


#-------SIDEBAR--------------------

with st.sidebar:
    """# Axes and gridlines"""
    xlowercol, xuppercol, xunitcol = st.columns(3)
    with xlowercol:
        xuserlowerinput = st.number_input("Lower x:", value=-2.0)
    with xuppercol:
        xuserupperinput = st.number_input("Upper x:", value=8.0)
    with xunitcol:
        x_is_pi = st.segmented_control("x unit:", options = ["1", "π"], default = '1', key="unit_control_1")
    xuserlower = xuserlowerinput * (PI if x_is_pi == "π" else 1)
    xuserupper = xuserupperinput * (PI if x_is_pi == "π" else 1)
    
    ylowercol, yuppercol, yunitcol = st.columns(3)
    with ylowercol:
        yuserlowerinput = st.number_input("Lower y:", value=-2.0)
    with yuppercol:
        yuserupperinput = st.number_input("Upper y:", value=8.0)
    with yunitcol:
        y_is_pi = st.segmented_control("y unit:", options = ["1", "π"], default = '1', key="unit_control_2")
    yuserlower = yuserlowerinput * (PI if y_is_pi == "π" else 1)
    yuserupper = yuserupperinput * (PI if y_is_pi == "π" else 1)
    
    xdifference = xuserupper - xuserlower
    ydifference = yuserupper - yuserlower
    xlower = xuserlower - 0.025 * xdifference
    xupper = xuserupper + 0.025 * xdifference
    ylower = yuserlower - 0.025 * ydifference
    yupper = yuserupper + 0.025 * ydifference
    
    showvalues = st.checkbox("Show values on axes", value=True)
    
    if showvalues:
        xstepcol, ystepcol = st.columns(2)
        with xstepcol:
            x_base_step = st.number_input("x-axis step:", value=2)
            xstep = x_base_step * (PI if x_is_pi == "π" else 1)
        with ystepcol:
            y_base_step = st.number_input("y-axis step:", value=2)
            ystep = y_base_step * (PI if y_is_pi == "π" else 1)
        label_size = st.slider("Label size", min_value=12, max_value=26, value=20, step=1)
    else:
        xstep = 1
        ystep = 1
        label_size = 20

    gridstyle = st.segmented_control("Gridlines", options = ["None", "Major", "Minor"], default = 'None')

    if gridstyle == 'Minor':
        xdivcol, ydivcol = st.columns(2)
        with xdivcol:
            xminordivisor = st.number_input("Minor divisor for x:", value=4)
        with ydivcol:
            yminordivisor = st.number_input("Minor divisor for y:", value=4)
    else:
        xminordivisor = 1
        yminordivisor = 1

    if not gridstyle:
        gridstyle = "None"

    """# Appearance"""
    axis_weight = st.slider("Axis weight", min_value=1.5, max_value=4.0, value=3.0, step=0.5)

    heightcol, widthcol = st.columns(2)
    with heightcol:
        imageheight = st.number_input("Height", value=8)
    with widthcol:
        imagewidth = st.number_input("Width", value=10)

    st.write("")  # Adds vertical space
    white_background = st.toggle("White background", value=True)


#-------INITIAL PLOT-------------------------

x_init = np.linspace(xlower, xupper, 100000)
y_init = np.zeros_like(x_init)  # Create corresponding y values

fig, ax = create_graph(
    xlower=xlower,
    xupper=xupper,
    ylower=ylower,
    yupper=yupper,
    xstep=xstep,
    ystep=ystep,
    gridstyle=gridstyle,
    xminordivisor=xminordivisor,
    yminordivisor=yminordivisor,
    imagewidth=imagewidth,
    imageheight=imageheight,
    xuserlower=xuserlower,
    xuserupper=xuserupper,
    yuserlower=yuserlower,
    yuserupper=yuserupper,
    showvalues=showvalues,
    axis_weight=axis_weight,
    label_size=label_size,
    white_background=white_background,
    skip_static_plots=False  # or True if you want to skip plotting static data
)

ax.plot(x_init, y_init, alpha=0)  # Plot invisible points
ax.margins(x=0, y=0)  # Remove margins
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)  # Remove all padding
ax.set_xlim(xlower, xupper)  # Force exact limits
ax.set_ylim(ylower, yupper)  # Force exact limits


#-------ADD FUNCTIONS-------------------------

if "plotted_functions" not in st.session_state:
    st.session_state.plotted_functions = []  # List to store function data

if "plotted_points" not in st.session_state:
    st.session_state.plotted_points = []

if "plot_data" not in st.session_state:
    st.session_state.plot_data = {"x": None, "y": None, "function": None}

if "selected_color" not in st.session_state:
    st.session_state.selected_color = "blue"  # Default color

if "selected_line_style" not in st.session_state:
    st.session_state.selected_line_style = "-"  # Default line style

if "plotted_implicit_functions" not in st.session_state:
    st.session_state.plotted_implicit_functions = []

if "plotted_parametric_functions" not in st.session_state:
    st.session_state.plotted_parametric_functions = []

if "plot_counter" not in st.session_state:
    st.session_state.plot_counter = 0

for i in range(5):
    if f"point_color_{i}" not in st.session_state:
        st.session_state[f"point_color_{i}"] = "blue"
    if f"point_style_{i}" not in st.session_state:
        st.session_state[f"point_style_{i}"] = "×"  # Default to cross marker


master_col1, master_col2 = st.columns([1.5, 1])

with master_col1:
    plot_placeholder = st.empty()
    st.write("")
    download_columns = st.columns([1.2, 1, 1, 1])
    with download_columns[1]:
        svg_placeholder = st.empty()
    with download_columns[2]:
        png_placeholder = st.empty()

with master_col2:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Explicit functions", "Implicit functions", "Parametric functions", "Points", "Areas"])
    
    with tab1:
        st.subheader("Plot explicit functions", divider="gray")
        
        # Initialize conversion variables
        python_str = None
        preview_expr = None
        
        # Input row
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
        
        with col1:
            latex_input = st.text_input(f"Function 1", 
                                      value=r"\frac{x}{2}-\sin(x)",
                                      key=f"latex_function_1")
        
        with col2:
            color_choice = st.selectbox("Color", 
                                      options=list(MY_COLORS.keys()), 
                                      key=f"latex_color_1",
                                      index=0,
                                      label_visibility="collapsed")
        
        with col3:
            line_styles = ("solid", "dashed", "dotted")
            line_style_choice = st.selectbox("Line style", 
                                           line_styles,
                                           key=f"latex_style_1",
                                           index=0,
                                           label_visibility="collapsed")
            
            line_style = {
                "solid": "-",
                "dashed": "--",
                "dotted": ":"
            }[line_style_choice]
        
        # Do LaTeX conversion here so python_str is available for plot button
        if latex_input.strip():
            python_str, preview_expr = latex_to_python(latex_input)
        
        with col4:
            if st.button("Plot", key=f"latex_plot_1"):
                if latex_input.strip() and python_str:
                    x = np.linspace(xlower, xupper, 100000)
                    y = eval_function(python_str, x, np, ylower, yupper)
                    
                    st.session_state.plot_counter += 1
                    func_data = {
                        "x": x,
                        "y": y,
                        "function": python_str,
                        "color": color_choice,
                        "line_style": line_style,
                        "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                    }
                    
                    if 0 < len(st.session_state.plotted_functions):
                        st.session_state.plotted_functions[0] = func_data
                    else:
                        st.session_state.plotted_functions.append(func_data)

        # Add remaining 4 function inputs
        for i in range(2, 6):  # Functions 2-5
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                latex_input_i = st.text_input(f"Function {i}", 
                                            value="",
                                            key=f"latex_function_{i}")
            
            with col2:
                color_choice_i = st.selectbox("Color", 
                                            options=list(MY_COLORS.keys()), 
                                            key=f"latex_color_{i}",
                                            index=0,
                                            label_visibility="collapsed")
            
            with col3:
                line_style_choice_i = st.selectbox("Line style", 
                                                 line_styles,
                                                 key=f"latex_style_{i}",
                                                 index=0,
                                                 label_visibility="collapsed")
                
                line_style_i = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice_i]
            
            # Do LaTeX conversion
            python_str_i = None
            if latex_input_i.strip():
                python_str_i, _ = latex_to_python(latex_input_i)
            
            with col4:
                if st.button("Plot", key=f"latex_plot_{i}"):
                    if latex_input_i.strip() and python_str_i:
                        x = np.linspace(xlower, xupper, 100000)
                        y = eval_function(python_str_i, x, np, ylower, yupper)
                        
                        st.session_state.plot_counter += 1
                        func_data = {
                            "x": x,
                            "y": y,
                            "function": python_str_i,
                            "color": color_choice_i,
                            "line_style": line_style_i,
                            "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                        }
                        
                        if i-1 < len(st.session_state.plotted_functions):
                            st.session_state.plotted_functions[i-1] = func_data
                        else:
                            st.session_state.plotted_functions.append(func_data)
                            
        st.caption("Enter functions of $x$ in latex.")

    with tab2:
        st.subheader("Plot implicit functions", divider="gray")
        
        # Create up to 5 implicit function input rows
        for i in range(5):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                default_value = r"x^2 + y^2 - 1" if i == 0 else ""
                latex_input = st.text_input(f"Function {i+1}", 
                                     value=default_value,
                                     key=f"implicit_latex_{i}")
            
            with col2:
                color_choice = st.selectbox("Color", 
                                      options=list(MY_COLORS.keys()), 
                                      key=f"implicit_color_{i}",
                                      index=0,
                                      label_visibility="collapsed")
            
            with col3:
                line_styles = ("solid", "dashed", "dotted")
                line_style_choice = st.selectbox("Line style", 
                                               line_styles,
                                               key=f"implicit_style_{i}",
                                               index=0,
                                               label_visibility="collapsed")
                
                line_style = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice]
            
            # Do LaTeX conversion here so python_str is available for plot button
            python_str = None
            if latex_input.strip():
                python_str, _ = latex_to_python(latex_input)
            
            with col4:
                if st.button("Plot", key=f"plot_implicit_{i}"):
                    if latex_input.strip() and python_str:
                        st.session_state.plot_counter += 1
                        implicit_data = {
                            "function": python_str,
                            "color": color_choice,
                            "line_style": line_style,
                            "zorder": 10 + st.session_state.plot_counter  # Base zorder of 10 for all functions
                        }
                        
                        if i < len(st.session_state.plotted_implicit_functions):
                            st.session_state.plotted_implicit_functions[i] = implicit_data
                        else:
                            st.session_state.plotted_implicit_functions.append(implicit_data)

        st.caption("Entering $f(x,y)$ will plot the curve $f(x,y) = 0$.\n\nFor example, $x^2 + y^2 - 1$ plots the unit circle.")

    with tab3:
        st.subheader("Plot parametric functions", divider="gray")
        
        # Create up to 5 parametric function input rows
        for i in range(5):
            # All controls in one row with minimum widths
            col1, col2, col3, col4, col5, col6 = st.columns([3.5, 3.5, 2, 2, 2, 1.5], vertical_alignment="bottom")
            with col1:
                default_x = r"\cos(t)" if i == 0 else ""
                x_latex = st.text_input(f"Function {i+1}",
                                      value=default_x,
                                      key=f"param_x_latex_{i}")
            with col2:
                default_y = r"\sin(t)" if i == 0 else ""
                y_latex = st.text_input(" ",  # Invisible label
                                      value=default_y,
                                      key=f"param_y_latex_{i}")
            with col3:
                t_range = st.text_input(" ",  # Invisible label
                                      value=r"-\pi:\pi" if i == 0 else "",
                                      key=f"param_range_{i}")
            with col4:
                color_choice = st.selectbox(" ",  # Invisible label
                                          options=list(MY_COLORS.keys()), 
                                          key=f"param_color_{i}",
                                          index=0,
                                          label_visibility="collapsed")
            
            with col5:
                line_styles = ("solid", "dashed", "dotted")
                line_style_choice = st.selectbox(" ",  # Invisible label
                                               line_styles,
                                               key=f"param_style_{i}",
                                               index=0,
                                               label_visibility="collapsed")
                line_style = {
                    "solid": "-",
                    "dashed": "--",
                    "dotted": ":"
                }[line_style_choice]
            
            # Convert LaTeX before plot button
            x_python = None
            y_python = None
            if x_latex.strip() and y_latex.strip():
                x_python, _ = latex_to_python(x_latex, param_var='t')
                y_python, _ = latex_to_python(y_latex, param_var='t')
            
            with col6:
                if st.button("Plot", key=f"plot_param_{i}"):
                    if x_python and y_python and t_range:
                        try:
                            # Parse t range with better LaTeX handling
                            t_start, t_end = t_range.split(":")
                            
                            # Convert start and end values from LaTeX if needed
                            t_start_python, _ = latex_to_python(t_start)
                            t_end_python, _ = latex_to_python(t_end)
                            
                            # Replace π with PI constant and evaluate
                            t_start = float(eval(t_start_python.replace("π", str(PI))))
                            t_end = float(eval(t_end_python.replace("π", str(PI))))
                            
                            # Create t values
                            t = np.linspace(t_start, t_end, 1000)
                            
                            # Evaluate x(t) and y(t)
                            x = eval_function(x_python, t, np, param_var='t')
                            y = eval_function(y_python, t, np, param_var='t')
                            
                            st.session_state.plot_counter += 1
                            param_data = {
                                "x": x,
                                "y": y,
                                "function": (x_python, y_python),
                                "color": color_choice,
                                "line_style": line_style,
                                "zorder": 10 + st.session_state.plot_counter
                            }
                            
                            if i < len(st.session_state.plotted_parametric_functions):
                                st.session_state.plotted_parametric_functions[i] = param_data
                            else:
                                st.session_state.plotted_parametric_functions.append(param_data)
                        except Exception as e:
                            st.error(f"Error plotting parametric function: {str(e)}")
            
            # Add some space between functions
            st.write("")

        st.caption("Enter latex functions $x(t)$ and $y(t)$ along with a latex domain in the format start:end.")

    with tab4:
        st.subheader("Plot points", divider="gray")
        
        # Create up to 5 point input rows
        for i in range(5):
            col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1, 1, 1], vertical_alignment="bottom")
            
            with col1:
                x_coord = st.number_input(f"x{i+1}", key=f"point_x_{i}")
            
            with col2:
                y_coord = st.number_input(f"y{i+1}", key=f"point_y_{i}")
                
            with col3:
                point_color = st.selectbox("Color", 
                                         options=list(MY_COLORS.keys()), 
                                         key=f"point_color_{i}",
                                         label_visibility="collapsed")
            
            with col4:
                marker_style = st.selectbox("Style", 
                                          ("×", "○"), 
                                          key=f"point_style_{i}",
                                          label_visibility="collapsed")
                marker = "x" if marker_style == "×" else "o"
            
            with col5:
                if st.button("Plot", key=f"plot_point_{i}"):
                    point_data = {
                        "x": x_coord,
                        "y": y_coord,
                        "marker": marker,
                        "color": point_color
                    }
                    
                    if i < len(st.session_state.plotted_points):
                        st.session_state.plotted_points[i] = point_data
                    else:
                        st.session_state.plotted_points.append(point_data)

    with tab5:  # New "Areas" tab
        st.subheader("Plot areas", divider="gray")
        
        # Get list of all plotted functions for selection
        explicit_functions = [f"Explicit {i+1}" 
                             for i, func in enumerate(st.session_state.plotted_functions)
                             if func is not None]
        
        implicit_functions = [f"Implicit {i+1}"
                             for i, func in enumerate(st.session_state.plotted_implicit_functions)
                             if func is not None]
        
        parametric_functions = [f"Parametric {i+1}"
                               for i, func in enumerate(st.session_state.plotted_parametric_functions)
                               if func is not None]
        
        all_functions = explicit_functions + implicit_functions + parametric_functions
        
        col1, col2, col3, col4 = st.columns([4, 4, 2, 2])
        with col1:
            upper_func_idx = st.selectbox("Upper function", 
                                        options=all_functions,
                                        index=0 if all_functions else None)
        with col2:
            lower_func_idx = st.selectbox("Lower function", 
                                        options=["x-axis"] + all_functions,
                                        index=0)
        with col3:
            x_start = st.number_input("From x =", value=xuserlower)
        with col4:
            x_end = st.number_input("To x =", value=xuserupper)
        
        color_col, alpha_col, plot_col = st.columns([2, 2, 1])
        with color_col:
            fill_color = st.selectbox("Fill color", options=list(MY_COLORS.keys()))
        with alpha_col:
            opacity = st.slider("Opacity", 0.0, 1.0, 0.3)
        with plot_col:
            if st.button("Fill Area"):
                if upper_func_idx:
                    try:
                        # Get x values for the fill
                        x_fill = np.linspace(x_start, x_end, 1000)
                        
                        # Initialize y arrays
                        upper_y = None
                        lower_y = None
                        
                        # Get upper function data
                        if upper_func_idx.startswith("Explicit"):
                            idx = int(upper_func_idx.split()[1]) - 1
                            upper_y = eval_function(st.session_state.plotted_functions[idx]["function"], x_fill, np, ylower, yupper)
                            st.write(f"Debug: Upper function type: Explicit")
                            st.write(f"Debug: Upper function values: min={np.min(upper_y):.2f}, max={np.max(upper_y):.2f}")
                        elif upper_func_idx.startswith("Parametric"):
                            idx = int(upper_func_idx.split()[1]) - 1
                            param_data = st.session_state.plotted_parametric_functions[idx]
                            st.write(f"Debug: Upper function type: Parametric")
                            st.write(f"Debug: Parametric x range: {np.min(param_data['x']):.2f} to {np.max(param_data['x']):.2f}")
                            st.write(f"Debug: Parametric y range: {np.min(param_data['y']):.2f} to {np.max(param_data['y']):.2f}")
                            
                            # Sort x and y values to ensure proper interpolation
                            sort_idx = np.argsort(param_data["x"])
                            x_sorted = param_data["x"][sort_idx]
                            y_sorted = param_data["y"][sort_idx]
                            
                            # Interpolate y values for our x_fill points
                            upper_y = np.interp(x_fill, x_sorted, y_sorted, left=np.nan, right=np.nan)
                            st.write(f"Debug: Interpolated upper y range: {np.nanmin(upper_y):.2f} to {np.nanmax(upper_y):.2f}")
                        elif upper_func_idx.startswith("Implicit"):
                            idx = int(upper_func_idx.split()[1]) - 1
                            implicit_data = st.session_state.plotted_implicit_functions[idx]
                            st.write(f"Debug: Upper function type: Implicit")
                            
                            # Create grid of points
                            x = np.linspace(xlower, xupper, 1000)
                            y = np.linspace(ylower, yupper, 1000)
                            X, Y = np.meshgrid(x, y)
                            
                            # Evaluate the implicit function
                            x_sym, y_sym = sp.symbols('x y')
                            expr = eval(implicit_data["function"], {
                                "x": x_sym, 
                                "y": y_sym, 
                                "lib": sp
                            })
                            
                            # Convert to numpy function and evaluate
                            f = sp.lambdify((x_sym, y_sym), expr)
                            Z = f(X, Y)
                            
                            # Find contour at level 0
                            contours = plt.contour(X, Y, Z, levels=[0])
                            plt.clf()  # Clear the temporary contour plot
                            
                            # Get the points from the contour
                            contour_paths = contours.collections[0].get_paths()
                            
                            if len(contour_paths) > 0:
                                # Get the first path (we might need to handle multiple paths later)
                                path = contour_paths[0]
                                vertices = path.vertices
                                
                                # Sort points by x coordinate for interpolation
                                sort_idx = np.argsort(vertices[:, 0])
                                x_sorted = vertices[sort_idx, 0]
                                y_sorted = vertices[sort_idx, 1]
                                
                                # Interpolate y values for our x_fill points
                                upper_y = np.interp(x_fill, x_sorted, y_sorted, left=np.nan, right=np.nan)
                                st.write(f"Debug: Implicit contour found")
                                st.write(f"Debug: Contour y range: {np.nanmin(upper_y):.2f} to {np.nanmax(upper_y):.2f}")
                            else:
                                st.error("No contour found for implicit function")
                                upper_y = np.zeros_like(x_fill)
                        
                        # Get lower function data with similar debugging
                        if lower_func_idx == "x-axis":
                            lower_y = np.zeros_like(x_fill)
                            st.write("Debug: Lower function: x-axis (zeros)")
                        elif lower_func_idx.startswith("Explicit"):
                            idx = int(lower_func_idx.split()[1]) - 1
                            lower_y = eval_function(st.session_state.plotted_functions[idx]["function"], x_fill, np, ylower, yupper)
                            st.write(f"Debug: Lower function type: Explicit")
                            st.write(f"Debug: Lower function values: min={np.min(lower_y):.2f}, max={np.max(lower_y):.2f}")
                        elif lower_func_idx.startswith("Parametric"):
                            idx = int(lower_func_idx.split()[1]) - 1
                            param_data = st.session_state.plotted_parametric_functions[idx]
                            # Sort x and y values to ensure proper interpolation
                            sort_idx = np.argsort(param_data["x"])
                            x_sorted = param_data["x"][sort_idx]
                            y_sorted = param_data["y"][sort_idx]
                            # Interpolate y values for our x_fill points
                            lower_y = np.interp(x_fill, x_sorted, y_sorted, left=np.nan, right=np.nan)
                        elif lower_func_idx.startswith("Implicit"):
                            idx = int(lower_func_idx.split()[1]) - 1
                            lower_y = np.zeros_like(x_fill)  # Placeholder
                        
                        # Check if we have valid data
                        if upper_y is not None and lower_y is not None:
                            # Remove any NaN values before filling
                            valid_mask = ~(np.isnan(upper_y) | np.isnan(lower_y))
                            st.write(f"Debug: Valid points: {np.sum(valid_mask)} out of {len(valid_mask)}")
                            
                            if np.any(valid_mask):
                                ax.fill_between(x_fill[valid_mask], 
                                              lower_y[valid_mask], 
                                              upper_y[valid_mask],
                                              color=MY_COLORS[fill_color],
                                              alpha=opacity,
                                              zorder=20)  # Increased zorder to be above most elements
                                st.write("Debug: Fill between called")
                                st.write(f"Debug: Fill color: {fill_color}, alpha: {opacity}")
                                st.write(f"Debug: x range: {x_fill[valid_mask].min():.2f} to {x_fill[valid_mask].max():.2f}")
                                st.write(f"Debug: y ranges: {lower_y[valid_mask].min():.2f} to {upper_y[valid_mask].max():.2f}")
                            else:
                                st.error("No valid points found for filling")
                        else:
                            st.error("Could not compute function values")
                            
                    except Exception as e:
                        st.error(f"Error filling area: {str(e)}")

for func_data in st.session_state.plotted_functions:
    if "zorder" not in func_data:
        st.session_state.plot_counter += 1
        func_data["zorder"] = st.session_state.plot_counter
    
    ax.plot(
        func_data["x"],
        func_data["y"],
        color=MY_COLORS[func_data["color"]],
        linestyle=func_data["line_style"],
        linewidth=axis_weight * 1.3,
        zorder=func_data["zorder"])

for point_data in st.session_state.plotted_points:
    if "zorder" not in point_data:
        st.session_state.plot_counter += 1
        point_data["zorder"] = st.session_state.plot_counter
        
    if point_data["marker"] == "x":
        markersize = axis_weight * 6
        markeredgewidth = axis_weight
    else:  # circle
        markersize = axis_weight * 3
        markeredgewidth = axis_weight
    
    ax.plot(point_data["x"], 
           point_data["y"], 
           marker=point_data["marker"],
           color=MY_COLORS[point_data["color"]], 
           markersize=markersize,
           markeredgewidth=markeredgewidth,
           linestyle='none',
           zorder=point_data["zorder"])

# Plot all stored implicit functions
for implicit_data in st.session_state.plotted_implicit_functions:
    if implicit_data and implicit_data["function"].strip():
        if "zorder" not in implicit_data:
            st.session_state.plot_counter += 1
            implicit_data["zorder"] = st.session_state.plot_counter
            
        x = np.linspace(xlower, xupper, 1000)
        y = np.linspace(ylower, yupper, 1000)
        X, Y = np.meshgrid(x, y)
        
        # Evaluate the expression
        x_sym, y_sym = sp.symbols('x y')
        expr = eval(implicit_data["function"], {
            "x": x_sym, 
            "y": y_sym, 
            "lib": sp  # This is what users expect to use
        })
        
        # Convert to numpy function and plot
        f = sp.lambdify((x_sym, y_sym), expr)
        Z = f(X, Y)
        
        ax.contour(X, Y, Z, levels=[0], 
                  colors=[MY_COLORS[implicit_data["color"]]],
                  linestyles=[implicit_data["line_style"]],
                  linewidths=axis_weight * 1.3,
                  zorder=implicit_data["zorder"])

for param_data in st.session_state.plotted_parametric_functions:
    if param_data:
        ax.plot(
            param_data["x"],
            param_data["y"],
            color=MY_COLORS[param_data["color"]],
            linestyle=param_data["line_style"],
            linewidth=axis_weight * 1.3,
            zorder=param_data["zorder"])

if not white_background:
    ax.set_facecolor('none')  # Transparent background
    fig.patch.set_facecolor('none')  # Transparent figure background

plot_placeholder.pyplot(fig)


#-------SAVE IMAGES-------------------------

svg_buffer = io.StringIO()
fig.savefig(svg_buffer, format="svg")
svg_data = svg_buffer.getvalue()
svg_buffer.close()

svg_placeholder.download_button(
    label="Download SVG",
    data=svg_data,
    file_name="figure1.svg",
    mime="image/svg+xml",
)

png_buffer = io.BytesIO()
fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
png_buffer.seek(0)
png_data = png_buffer.getvalue()
png_buffer.close()

png_placeholder.download_button(
    label = "Download PNG", 
    data=png_data, 
    file_name="figure1.png", 
    mime="image/png")


#-------unused-------

# latex_preview = sp.latex(y1_sym)  # Convert to LaTeX
# st.latex(f"y = {latex_preview}")  # Display LaTeX preview
