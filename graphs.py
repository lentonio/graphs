import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sympy as sp
from sympy import nsimplify, pi, latex
import streamlit as st
import io

from graph_utils import create_graph, eval_function

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
        label_size = st.slider("Label size", min_value=12, max_value=26, value=16, step=1)
    else:
        xstep = 1
        ystep = 1
        label_size = 16

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
    axis_weight = st.slider("Axis weight", min_value=1.5, max_value=4.0, value=2.0, step=0.5)

    heightcol, widthcol = st.columns(2)
    with heightcol:
        imageheight = st.number_input("Height", value=8)
    with widthcol:
        imagewidth = st.number_input("Width", value=10)


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
    st.subheader("Plot functions", divider="gray")
    
    # Create up to 5 function input rows
    for i in range(5):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
        
        with col1:
            default_value = "0.1 * x**2 * lib.sin(3*x)" if i == 0 else ""
            user_input = st.text_input(f"Function {i+1}", 
                                     value=default_value,
                                     key=f"function_{i}")
            if user_input.strip():
                x_sym = sp.Symbol('x')
                y1_sym = eval_function(user_input, x_sym, sp)
                y1_sym = sp.nsimplify(y1_sym)
        
        with col2:
            # Initialize color in session state if not present
            if f"selected_color_{i}" not in st.session_state:
                st.session_state[f"selected_color_{i}"] = "blue"  # default color
            
            color_choice = st.selectbox("Color", 
                                      options=list(MY_COLORS.keys()), 
                                      key=f"color_{i}",
                                      index=list(MY_COLORS.keys()).index(st.session_state[f"selected_color_{i}"]),
                                      label_visibility="collapsed")
            st.session_state[f"selected_color_{i}"] = color_choice
        
        with col3:
            # Initialize line style in session state if not present
            if f"selected_line_style_{i}" not in st.session_state:
                st.session_state[f"selected_line_style_{i}"] = "solid"  # default style
            
            line_styles = ("solid", "dashed", "dotted")
            line_style_choice = st.selectbox("Line style", 
                                           line_styles,
                                           key=f"style_{i}",
                                           index=line_styles.index(st.session_state[f"selected_line_style_{i}"]),
                                           label_visibility="collapsed")
            st.session_state[f"selected_line_style_{i}"] = line_style_choice
            
            # Convert to matplotlib style
            line_style = {
                "solid": "-",
                "dashed": "--",
                "dotted": ":"
            }[line_style_choice]
    
        with col4:
                if st.button("Plot", key=f"plot_{i}"):
                    # Only plot if there's a function entered
                    if user_input.strip():
                        x = np.linspace(xlower, xupper, 100000)
                        y = eval_function(user_input, x, np, ylower, yupper)
                        
                        # Create function data dictionary
                        func_data = {
                            "x": x,
                            "y": y,
                            "function": user_input,
                            "color": st.session_state[f"selected_color_{i}"],
                            "line_style": line_style
                        }
                        
                        # Update or add the function data in our list
                        if i < len(st.session_state.plotted_functions):
                            st.session_state.plotted_functions[i] = func_data
                        else:
                            st.session_state.plotted_functions.append(func_data)


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

for func_data in st.session_state.plotted_functions:
    ax.plot(
        func_data["x"],
        func_data["y"],
        color=MY_COLORS[func_data["color"]],
        linestyle=func_data["line_style"],
        linewidth=axis_weight * 1.3,
        zorder=3)

for point_data in st.session_state.plotted_points:
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
           zorder=3)

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
