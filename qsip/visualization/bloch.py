__all__ = ['Bloch', 'QuantumState']

import os
from typing import Literal, Union, List, Tuple
import numpy as np
from numpy import cos, ones, outer, sin
from packaging.version import parse as parse_version

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import Axes3D, proj3d

    # Define a custom _axes3D function based on the matplotlib version.
    # The auto_add_to_figure keyword is new for matplotlib>=3.4.
    if parse_version(matplotlib.__version__) >= parse_version('3.4'):
        def _axes3D(fig, *args, **kwargs):
            ax = Axes3D(fig, *args, auto_add_to_figure=False, **kwargs)
            return fig.add_axes(ax)
    else:
        def _axes3D(*args, **kwargs):
            return Axes3D(*args, **kwargs)

    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)

        def do_3d_projection(self, renderer=None):
            # only called by matplotlib >= 3.5
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            return np.min(zs)
except ImportError:
    pass

try:
    from IPython.display import display
except ImportError:
    pass


class QuantumState:
    """Simple quantum state representation for qubit states."""
    
    def __init__(self, state_vector: np.ndarray = None, density_matrix: np.ndarray = None):
        """
        Initialize a quantum state with either a state vector or density matrix.
        
        Parameters
        ----------
        state_vector : np.ndarray, optional
            Complex vector representing a pure quantum state
        density_matrix : np.ndarray, optional
            Density matrix representation of the quantum state
        """
        if state_vector is not None:
            self.state_vector = np.asarray(state_vector, dtype=complex)
            self.is_pure = True
            # Normalize the state vector
            norm = np.linalg.norm(self.state_vector)
            if norm > 0:
                self.state_vector = self.state_vector / norm
            # Create density matrix from state vector
            self.density_matrix = np.outer(self.state_vector, np.conj(self.state_vector))
        elif density_matrix is not None:
            self.density_matrix = np.asarray(density_matrix, dtype=complex)
            self.is_pure = np.allclose(np.trace(self.density_matrix @ self.density_matrix), 1.0)
            self.state_vector = None
        else:
            raise ValueError("Must provide either state_vector or density_matrix")
    
    def expectation(self, operator: np.ndarray) -> float:
        """Calculate expectation value of an operator."""
        if self.is_pure and self.state_vector is not None:
            return np.real(np.conj(self.state_vector) @ operator @ self.state_vector)
        else:
            return np.real(np.trace(operator @ self.density_matrix))


# Pauli matrices
def pauli_x():
    """Pauli X matrix (sigma_x)"""
    return np.array([[0, 1], [1, 0]], dtype=complex)


def pauli_y():
    """Pauli Y matrix (sigma_y)"""
    return np.array([[0, -1j], [1j, 0]], dtype=complex)


def pauli_z():
    """Pauli Z matrix (sigma_z)"""
    return np.array([[1, 0], [0, -1]], dtype=complex)


def _state_to_cartesian_coordinates(state: Union[QuantumState, np.ndarray, list, tuple]) -> List[float]:
    """Convert a quantum state to Bloch sphere coordinates."""
    if isinstance(state, (list, tuple)):
        # Already in Cartesian coordinates
        return list(state)
    elif isinstance(state, np.ndarray):
        if state.shape == (3,):
            # Already a Bloch vector
            return list(state)
        else:
            # Convert numpy array to QuantumState
            if state.ndim == 1:
                state = QuantumState(state_vector=state)
            else:
                state = QuantumState(density_matrix=state)
    
    if isinstance(state, QuantumState):
        x = state.expectation(pauli_x())
        y = state.expectation(pauli_y())
        z = state.expectation(pauli_z())
        return [x, y, z]
    else:
        raise ValueError("Invalid state type")


class Bloch:
    r"""
    Class for plotting data on the Bloch sphere. Valid data can be either
    points, vectors, or quantum states.

    Attributes
    ----------
    axes : matplotlib.axes.Axes
        User supplied Matplotlib axes for Bloch sphere animation.
    fig : matplotlib.figure.Figure
        User supplied Matplotlib Figure instance for plotting Bloch sphere.
    font_color : str, default 'black'
        Color of font used for Bloch sphere labels.
    font_size : int, default 20
        Size of font used for Bloch sphere labels.
    frame_alpha : float, default 0.1
        Sets transparency of Bloch sphere frame.
    frame_color : str, default 'gray'
        Color of sphere wireframe.
    frame_width : int, default 1
        Width of wireframe.
    point_color : list, default ["b", "r", "g", "#CC6600"]
        List of colors for Bloch sphere point markers to cycle through.
    point_marker : list, default ["o", "s", "d", "^"]
        List of point marker shapes to cycle through.
    point_size : list, default [25, 32, 35, 45]
        List of point marker sizes.
    sphere_alpha : float, default 0.2
        Transparency of Bloch sphere itself.
    sphere_color : str, default '#FFDDDD'
        Color of Bloch sphere.
    figsize : list, default [7, 7]
        Figure size of Bloch sphere plot.
    vector_color : list, ["g", "#CC6600", "b", "r"]
        List of vector colors to cycle through.
    vector_width : int, default 5
        Width of displayed vectors.
    vector_style : str, default '-\|>'
        Vector arrowhead style.
    vector_mutation : int, default 20
        Width of vectors arrowhead.
    view : list, default [-60, 30]
        Azimuthal and Elevation viewing angles.
    xlabel : list, default ["$x$", ""]
        List of strings corresponding to +x and -x axes labels.
    xlpos : list, default [1.1, -1.1]
        Positions of +x and -x labels.
    ylabel : list, default ["$y$", ""]
        List of strings corresponding to +y and -y axes labels.
    ylpos : list, default [1.2, -1.2]
        Positions of +y and -y labels.
    zlabel : list, default ['$\\left\|0\\right>$', '$\\left\|1\\right>$']
        List of strings corresponding to +z and -z axes labels.
    zlpos : list, default [1.2, -1.2]
        Positions of +z and -z labels.
    """
    
    def __init__(self, fig=None, axes=None, view=None, figsize=None,
                 background=False):
        # Figure and axes
        self.fig = fig
        self._ext_fig = fig is not None
        self.axes = axes
        # Background axes, default = False
        self.background = background
        # The size of the figure in inches, default = [5,5].
        self.figsize = figsize if figsize else [5, 5]
        # Azimuthal and Elevation viewing angles, default = [-60,30].
        self.view = view if view else [-60, 30]
        
        # Enhanced visual settings for better aesthetics
        # Warmer, creamier white sphere
        self.sphere_color = '#FFF8E7'  # Creamy white with warm undertone
        self.sphere_alpha = 0.35  # Slightly more opaque for creamier appearance
        self.frame_color = '#8B7355'  # Warm brown for frame
        self.frame_width = 0.8  # Thinner frame lines
        self.frame_alpha = 0.2  # More subtle frame
        
        # Font settings with better typography
        self.font_color = '#4A4037'  # Warm dark brown
        self.font_size = 16  # Slightly smaller for cleaner look
        self.font_family = 'serif'  # Better for math rendering
        self.mathtext_fontset = 'cm'  # Computer Modern for LaTeX-like math
        
        # Labels with improved formatting and positioning
        self.show_axis_labels = True  # Control whether to show axis labels
        self.xlabel = [r'$\hat{x}$', '']  # Unit vector notation
        self.xlpos = [1.35, -1.35]  # Moved further out to avoid vector overlap
        self.ylabel = [r'$\hat{y}$', '']  # Unit vector notation
        self.ylpos = [1.35, -1.35]  # Moved further out to avoid vector overlap
        self.zlabel = [r'$|0⟩$', r'$|1⟩$']  # Using Unicode bracket for cleaner look
        self.zlpos = [1.35, -1.35]  # Moved further out to avoid vector overlap
        
        # Vector options with rich Morandi color scheme
        # Rich, saturated Morandi colors for better visibility
        self.vector_default_color = [
            '#C67856',  # Rich burnt sienna (warm terracotta)
            '#5C8A72',  # Deep sage green (forest undertone)
            '#8B7399',  # Rich mauve (deeper purple-grey)
            '#B56576',  # Deep dusty rose (more saturated)
            '#A68B5B',  # Rich ochre (golden brown)
            '#6B85A3',  # Deep steel blue (stormy blue)
        ]
        self.vector_color = []
        self.vector_width = 2.2  # Slightly thicker for rich appearance
        self.vector_style = '->'  # Sharp arrow style
        self.vector_mutation = 12  # Proportional arrowheads
        
        # Point options with rich Morandi colors (matching vectors)
        self.point_default_color = [
            '#C67856',  # Rich burnt sienna
            '#5C8A72',  # Deep sage green
            '#8B7399',  # Rich mauve
            '#B56576',  # Deep dusty rose
        ]
        self.point_color = None
        self._inner_point_color = []
        self.point_size = [20, 25, 28, 35]  # Slightly smaller points
        self.point_marker = ['o', 's', 'D', '^']
        
        # Data lists
        self.points = []
        self.vectors = []
        self.vector_alpha = []
        self.annotations = []
        self.savenum = 0
        self.point_style = []
        self.point_alpha = []
        self._lines = []
        self._arcs = []

    def set_label_convention(self, convention):
        """Set x, y and z labels according to one of conventions.

        Parameters
        ----------
        convention : string
            One of the following:
            - "original"
            - "xyz"
            - "sx sy sz"
            - "01"
            - "polarization jones"
            - "polarization jones letters"
            - "polarization stokes"
        """
        ketex = r"$|%s⟩$"  # Using Unicode bracket

        if convention == "original":
            self.xlabel = [r'$\hat{x}$', '']
            self.ylabel = [r'$\hat{y}$', '']
            self.zlabel = [r'$|0⟩$', r'$|1⟩$']
        elif convention == "xyz":
            self.xlabel = [r'$\hat{x}$', '']
            self.ylabel = [r'$\hat{y}$', '']
            self.zlabel = [r'$\hat{z}$', '']
        elif convention == "sx sy sz":
            self.xlabel = [r'$\hat{\sigma}_x$', '']
            self.ylabel = [r'$\hat{\sigma}_y$', '']
            self.zlabel = [r'$\hat{\sigma}_z$', '']
        elif convention == "01":
            self.xlabel = ['', '']
            self.ylabel = ['', '']
            self.zlabel = [r'$|0⟩$', r'$|1⟩$']
        elif convention == "polarization jones":
            self.xlabel = [ketex % r"\nearrow\!\!\swarrow",
                           ketex % r"\nwarrow\!\!\searrow"]
            self.ylabel = [ketex % r"\circlearrowleft", 
                           ketex % r"\circlearrowright"]
            self.zlabel = [ketex % r"\leftrightarrow", 
                           ketex % r"\updownarrow"]
        elif convention == "polarization jones letters":
            self.xlabel = [ketex % "D", ketex % "A"]
            self.ylabel = [ketex % "L", ketex % "R"]  
            self.zlabel = [ketex % "H", ketex % "V"]
        elif convention == "polarization stokes":
            self.ylabel = [r"$\nearrow\!\!\swarrow$",
                           r"$\nwarrow\!\!\searrow$"]
            self.zlabel = [r"$\circlearrowleft$", r"$\circlearrowright$"]
            self.xlabel = [r"$\leftrightarrow$", r"$\updownarrow$"]
        else:
            raise Exception("No such convention.")

    def __str__(self):
        s = ""
        s += "Bloch data:\n"
        s += "-----------\n"
        s += "Number of points:  " + str(len(self.points)) + "\n"
        s += "Number of vectors: " + str(len(self.vectors)) + "\n"
        s += "\n"
        s += "Bloch sphere properties:\n"
        s += "------------------------\n"
        s += "font_color:      " + str(self.font_color) + "\n"
        s += "font_size:       " + str(self.font_size) + "\n"
        s += "frame_alpha:     " + str(self.frame_alpha) + "\n"
        s += "frame_color:     " + str(self.frame_color) + "\n"
        s += "frame_width:     " + str(self.frame_width) + "\n"
        s += "point_default_color:" + str(self.point_default_color) + "\n"
        s += "point_marker:    " + str(self.point_marker) + "\n"
        s += "point_size:      " + str(self.point_size) + "\n"
        s += "sphere_alpha:    " + str(self.sphere_alpha) + "\n"
        s += "sphere_color:    " + str(self.sphere_color) + "\n"
        s += "figsize:         " + str(self.figsize) + "\n"
        s += "vector_default_color:" + str(self.vector_default_color) + "\n"
        s += "vector_width:    " + str(self.vector_width) + "\n"
        s += "vector_style:    " + str(self.vector_style) + "\n"
        s += "vector_mutation: " + str(self.vector_mutation) + "\n"
        s += "view:            " + str(self.view) + "\n"
        s += "xlabel:          " + str(self.xlabel) + "\n"
        s += "xlpos:           " + str(self.xlpos) + "\n"
        s += "ylabel:          " + str(self.ylabel) + "\n"
        s += "ylpos:           " + str(self.ylpos) + "\n"
        s += "zlabel:          " + str(self.zlabel) + "\n"
        s += "zlpos:           " + str(self.zlpos) + "\n"
        return s

    def _repr_png_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'png')
        plt.close(self.fig)
        return fig_data

    def _repr_svg_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'svg')
        plt.close(self.fig)
        return fig_data

    def clear(self):
        """Resets Bloch sphere data sets to empty."""
        self.points = []
        self.vectors = []
        self.point_style = []
        self.point_alpha = []
        self.vector_alpha = []
        self.annotations = []
        self.vector_color = []
        self.point_color = None
        self._lines = []
        self._arcs = []

    def add_points(self, points, meth: Literal['s', 'm', 'l'] = 's',
                   colors=None, alpha=1.0):
        """Add a list of data points to bloch sphere.

        Parameters
        ----------
        points : array_like
            Collection of data points.
        meth : {'s', 'm', 'l'}
            Type of points to plot, use 'm' for multicolored, 'l' for points
            connected with a line.
        colors : array_like
            Optional array with colors for the points.
        alpha : float, default=1.
            Transparency value for the points.
        """
        points = np.asarray(points)

        if points.ndim == 1:
            points = points[:, np.newaxis]

        if points.ndim != 2 or points.shape[0] != 3:
            raise ValueError("Points must be a 2D array with shape (3, n)")

        if meth not in ['s', 'm', 'l']:
            raise ValueError(f"Invalid method: {meth}")

        if meth == 's' and points.shape[1] == 1:
            points = np.append(points[:, :1], points, axis=1)

        self.point_style.append(meth)
        self.points.append(points)
        self.point_alpha.append(alpha)
        self._inner_point_color.append(colors)

    def add_states(self, state: Union[QuantumState, np.ndarray, List],
                   kind: Literal['vector', 'point'] = 'vector',
                   colors=None, alpha=1.0):
        """Add quantum state(s) to Bloch sphere.

        Parameters
        ----------
        state : QuantumState, np.ndarray, or list
            Input state(s) to add to the sphere.
        kind : {'vector', 'point'}
            Type of object to plot.
        colors : str or array_like
            Optional colors for the states.
        alpha : float, default=1.
            Transparency value.
        """
        if not isinstance(state, list):
            state = [state]

        if colors is not None:
            colors = np.asarray(colors)
            if colors.ndim == 0:
                colors = np.repeat(colors, len(state))
        else:
            colors = [None] * len(state)

        for k, st in enumerate(state):
            vec = _state_to_cartesian_coordinates(st)
            
            if kind == 'vector':
                self.add_vectors([vec], colors=[colors[k]], alpha=alpha)
            elif kind == 'point':
                self.add_points(vec, colors=[colors[k]], alpha=alpha)
            else:
                raise ValueError(f"Invalid kind: {kind}")

    def add_vectors(self, vectors, colors=None, alpha=1.0):
        """Add vectors to Bloch sphere.

        Parameters
        ----------
        vectors : array_like
            Array with vectors of unit length or smaller.
        colors : str or array_like
            Optional colors for the vectors.
        alpha : float, default=1.
            Transparency value.
        """
        vectors = np.asarray(vectors)

        if vectors.ndim == 1:
            vectors = vectors[np.newaxis, :]

        if vectors.ndim != 2 or vectors.shape[1] != 3:
            raise ValueError("Vectors must be a 2D array with shape (n, 3)")

        if colors is None:
            colors = [None] * vectors.shape[0]
        else:
            colors = np.asarray(colors)
            if colors.ndim == 0:
                colors = np.repeat(colors, vectors.shape[0])

        for k, vec in enumerate(vectors):
            self.vectors.append(vec)
            self.vector_alpha.append(alpha)
            self.vector_color.append(colors[k])

    def add_annotation(self, state_or_vector, text, **kwargs):
        """Add text annotation to Bloch sphere.

        Parameters
        ----------
        state_or_vector : QuantumState/array/list/tuple
            Position for the annotation.
        text : str
            Annotation text (can use LaTeX).
        kwargs :
            Options for matplotlib text.
        """
        vec = _state_to_cartesian_coordinates(state_or_vector)
        
        # Don't add default background box - let user decide
        
        self.annotations.append({
            'position': vec,
            'text': text,
            'opts': kwargs
        })
    
    def add_annotation_smart(self, state_or_vector, text, offset=0.3, **kwargs):
        """Add text annotation with smart positioning to avoid vectors.

        Parameters
        ----------
        state_or_vector : QuantumState/array/list/tuple
            Position for the annotation.
        text : str
            Annotation text (can use LaTeX).
        offset : float
            Distance to offset the text from the point.
        kwargs :
            Options for matplotlib text.
        """
        vec = np.array(_state_to_cartesian_coordinates(state_or_vector))
        
        # Normalize the vector
        vec_norm = np.linalg.norm(vec)
        if vec_norm > 0:
            vec_direction = vec / vec_norm
            # Position text along the vector direction but further out
            text_position = vec + offset * vec_direction
        else:
            # For center point, offset upward
            text_position = vec + np.array([0, 0, offset])
        
        # Don't add default background box - let user decide
        
        self.annotations.append({
            'position': text_position,
            'text': text,
            'opts': kwargs
        })

    def add_arc(self, start, end, fmt="b", steps=None, **kwargs):
        """Add an arc between two points on the sphere.

        Parameters
        ----------
        start : QuantumState or array-like
            Starting point.
        end : QuantumState or array-like
            Ending point.
        fmt : str, default: "b"
            Matplotlib format string.
        steps : int, optional
            Number of segments for the arc.
        """
        pt1 = _state_to_cartesian_coordinates(start)
        pt2 = _state_to_cartesian_coordinates(end)
        
        pt1 = np.asarray(pt1)
        pt2 = np.asarray(pt2)

        len1 = np.linalg.norm(pt1)
        len2 = np.linalg.norm(pt2)

        # Validation
        if len1 < 1e-12 or len2 < 1e-12:
            raise ValueError("Points too close to origin")
        elif abs(len1 - len2) > 1e-12:
            raise ValueError("Points not on same sphere")
        elif np.linalg.norm(pt1 - pt2) < 1e-12:
            raise ValueError("Points are identical")
        elif np.linalg.norm(pt1 + pt2) < 1e-12:
            raise ValueError("Points are antipodal")

        if steps is None:
            steps = max(2, int(np.linalg.norm(pt1 - pt2) * 100))

        t = np.linspace(0, 1, steps)
        line = pt1[:, np.newaxis] * t + pt2[:, np.newaxis] * (1 - t)
        arc = (line * len1 / np.linalg.norm(line, axis=0)).T

        # Handle visibility regions
        if len1 < 1 - 1e-12:
            self._arcs.append([np.array(arc), "inner", fmt, kwargs])
            return

        def get_plot_area(front: bool, norm: float):
            if front:
                return "front"
            if norm > 1 + 1e-12:
                return "rear"
            return "inner"

        def append_interpolation_point(point, part, norm: float):
            if point[0] != 0:
                t_edge = 1 / (1 - part[-1][0] / point[0])
                edge_point = part[-1] * t_edge + point * (1 - t_edge)
                edge_point = edge_point * norm / np.linalg.norm(edge_point)
                part.append(edge_point)
                return [edge_point, point]
            else:
                part.append(point)
                return [point]

        front = arc[0][0] >= 0
        part = []
        
        for point in arc:
            if (point[0] >= 0) == front:
                part.append(point)
                continue

            new_part = append_interpolation_point(point, part, len1)
            self._arcs.append([np.array(part), get_plot_area(front, len1), fmt, kwargs])
            part = new_part
            front = not front

        self._arcs.append([np.array(part), get_plot_area(front, len1), fmt, kwargs])

    def add_line(self, start, end, fmt="k", **kwargs):
        """Add a line segment between two points.

        Parameters
        ----------
        start : QuantumState or array-like
            Starting point.
        end : QuantumState or array-like  
            Ending point.
        fmt : str, default: "k"
            Matplotlib format string.
        """
        pt1 = _state_to_cartesian_coordinates(start)
        pt2 = _state_to_cartesian_coordinates(end)
        
        pt1 = np.asarray(pt1)
        pt2 = np.asarray(pt2)

        x = [pt1[1], pt2[1]]
        y = [-pt1[0], -pt2[0]]
        z = [pt1[2], pt2[2]]
        self._lines.append([[x, y, z], fmt, kwargs])

    def render(self):
        """Render the Bloch sphere and its data."""
        # Configure matplotlib for better math rendering
        import matplotlib
        matplotlib.rcParams['mathtext.fontset'] = self.mathtext_fontset
        matplotlib.rcParams['font.family'] = self.font_family
        
        if not self._ext_fig and not self._is_inline_backend():
            if self.fig is not None and not plt.fignum_exists(self.fig.number):
                self.fig = None
                self.axes = None

        if self.fig is None:
            self.fig = plt.figure(figsize=self.figsize)
            if self._is_inline_backend():
                plt.close(self.fig)

        if self.axes is None:
            self.axes = _axes3D(self.fig, azim=self.view[0], elev=self.view[1])

        self.axes.clear()
        self.axes.grid(False)
        
        if self.background:
            self.axes.set_xlim3d(-1.5, 1.5)
            self.axes.set_ylim3d(-1.5, 1.5)
            self.axes.set_zlim3d(-1.5, 1.5)
        else:
            self.axes.set_axis_off()
            self.axes.set_xlim3d(-1.0, 1.0)  # Increased from 0.7 to prevent cropping
            self.axes.set_ylim3d(-1.0, 1.0)
            self.axes.set_zlim3d(-1.0, 1.0)
            
        if parse_version(matplotlib.__version__) >= parse_version('3.3'):
            self.axes.set_box_aspect((1, 1, 1))

        self.plot_arcs("rear")
        self.plot_back()
        self.plot_points()
        self.plot_vectors()
        self.plot_lines()
        self.plot_arcs("inner")
        if not self.background:
            self.plot_axes()
        self.plot_front()
        self.plot_arcs("front")
        self.plot_axes_labels()
        self.plot_annotations()
        self.fig.canvas.draw()

    def plot_back(self):
        """Plot back half of sphere."""
        # High resolution for smooth sphere surface
        u_surf = np.linspace(0, np.pi, 50)
        v_surf = np.linspace(0, np.pi, 50)
        x_surf = outer(cos(u_surf), sin(v_surf))
        y_surf = outer(sin(u_surf), sin(v_surf))
        z_surf = outer(ones(np.size(u_surf)), cos(v_surf))
        
        # Plot smooth surface
        self.axes.plot_surface(x_surf, y_surf, z_surf, rstride=1, cstride=1,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha, antialiased=True)
        
        # Create wireframe with smooth arcs
        # Use more points for drawing smooth curves, but fewer grid lines
        u_grid = np.linspace(0, np.pi, 6)  # 5 longitude lines  
        v_grid = np.linspace(0, np.pi, 6)  # 5 latitude lines
        
        # High resolution for smooth arc drawing
        u_smooth = np.linspace(0, np.pi, 30)
        v_smooth = np.linspace(0, np.pi, 30)
        
        # Plot smooth latitude lines (circles)
        for i in range(1, len(v_grid)-1):  # Skip poles
            x_lat = cos(u_smooth) * sin(v_grid[i])
            y_lat = sin(u_smooth) * sin(v_grid[i])
            z_lat = ones(len(u_smooth)) * cos(v_grid[i])
            self.axes.plot(x_lat, y_lat, z_lat, 
                          color=self.frame_color, alpha=self.frame_alpha,
                          linewidth=self.frame_width)
        
        # Plot smooth longitude lines (meridians)
        for i in range(len(u_grid)):
            x_lon = cos(u_grid[i]) * sin(v_smooth)
            y_lon = sin(u_grid[i]) * sin(v_smooth)
            z_lon = cos(v_smooth)
            self.axes.plot(x_lon, y_lon, z_lon,
                          color=self.frame_color, alpha=self.frame_alpha,
                          linewidth=self.frame_width)

    def plot_front(self):
        """Plot front half of sphere."""
        # High resolution for smooth sphere surface
        u_surf = np.linspace(-np.pi, 0, 50)
        v_surf = np.linspace(0, np.pi, 50)
        x_surf = outer(cos(u_surf), sin(v_surf))
        y_surf = outer(sin(u_surf), sin(v_surf))
        z_surf = outer(ones(np.size(u_surf)), cos(v_surf))
        
        # Plot smooth surface
        self.axes.plot_surface(x_surf, y_surf, z_surf, rstride=1, cstride=1,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha, antialiased=True)
        
        # Create wireframe with smooth arcs (front half)
        u_grid = np.linspace(-np.pi, 0, 6)  # 5 longitude lines
        v_grid = np.linspace(0, np.pi, 6)  # 5 latitude lines
        
        # High resolution for smooth arc drawing
        u_smooth = np.linspace(-np.pi, 0, 30)
        v_smooth = np.linspace(0, np.pi, 30)
        
        # Plot smooth latitude lines (front semicircles)
        for i in range(1, len(v_grid)-1):  # Skip poles
            x_lat = cos(u_smooth) * sin(v_grid[i])
            y_lat = sin(u_smooth) * sin(v_grid[i])
            z_lat = ones(len(u_smooth)) * cos(v_grid[i])
            self.axes.plot(x_lat, y_lat, z_lat,
                          color=self.frame_color, alpha=self.frame_alpha,
                          linewidth=self.frame_width)
        
        # Plot smooth longitude lines (front meridians)
        for i in range(len(u_grid)):
            x_lon = cos(u_grid[i]) * sin(v_smooth)
            y_lon = sin(u_grid[i]) * sin(v_smooth)
            z_lon = cos(v_smooth)
            self.axes.plot(x_lon, y_lon, z_lon,
                          color=self.frame_color, alpha=self.frame_alpha,
                          linewidth=self.frame_width)

    def plot_axes(self):
        """Plot coordinate axes."""
        span = np.linspace(-1.0, 1.0, 2)
        self.axes.plot(span, 0 * span, zs=0, zdir='z', label='X',
                       lw=self.frame_width * 0.8, color=self.frame_color,
                       alpha=self.frame_alpha * 0.8)
        self.axes.plot(0 * span, span, zs=0, zdir='z', label='Y',
                       lw=self.frame_width * 0.8, color=self.frame_color,
                       alpha=self.frame_alpha * 0.8)
        self.axes.plot(0 * span, span, zs=0, zdir='y', label='Z',
                       lw=self.frame_width * 0.8, color=self.frame_color,
                       alpha=self.frame_alpha * 0.8)

    def plot_axes_labels(self):
        """Plot axis labels."""
        if not self.show_axis_labels:
            return
            
        opts = {
            'fontsize': self.font_size,
            'color': self.font_color,
            'horizontalalignment': 'center',
            'verticalalignment': 'center',
            'fontfamily': self.font_family,
            'bbox': dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor='none', alpha=0.7)  # Add background box
        }
        
        if self.xlabel[0]:  # Only show if not empty
            self.axes.text(0, -self.xlpos[0], 0, self.xlabel[0], **opts)
        if self.xlabel[1]:
            self.axes.text(0, -self.xlpos[1], 0, self.xlabel[1], **opts)
        if self.ylabel[0]:
            self.axes.text(self.ylpos[0], 0, 0, self.ylabel[0], **opts)
        if self.ylabel[1]:
            self.axes.text(self.ylpos[1], 0, 0, self.ylabel[1], **opts)
        if self.zlabel[0]:
            self.axes.text(0, 0, self.zlpos[0], self.zlabel[0], **opts)
        if self.zlabel[1]:
            self.axes.text(0, 0, self.zlpos[1], self.zlabel[1], **opts)

        for a in (self.axes.xaxis.get_ticklines() +
                  self.axes.xaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.yaxis.get_ticklines() +
                  self.axes.yaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.zaxis.get_ticklines() +
                  self.axes.zaxis.get_ticklabels()):
            a.set_visible(False)

    def plot_vectors(self):
        """Plot Bloch vectors."""
        for k, vec in enumerate(self.vectors):
            # Apply a small uniform extension to ensure vectors reach surface
            vec_extended = vec * 1.02
            xs3d = np.array([0, vec_extended[1]])
            ys3d = np.array([0, -vec_extended[0]])
            zs3d = np.array([0, vec_extended[2]])

            alpha = self.vector_alpha[k]
            color = self.vector_color[k]
            if color is None:
                idx = k % len(self.vector_default_color)
                color = self.vector_default_color[idx]

            a = Arrow3D(xs3d, ys3d, zs3d,
                        mutation_scale=self.vector_mutation,
                        lw=self.vector_width,
                        arrowstyle=self.vector_style,
                        color=color, alpha=alpha,
                        shrinkA=0, shrinkB=5)  # Small shrink at head only
            self.axes.add_artist(a)

    def plot_points(self):
        """Plot data points."""
        for k, points in enumerate(self.points):
            points = np.asarray(points)
            num_points = points.shape[1]

            dist = np.linalg.norm(points, axis=0)
            if not np.allclose(dist, dist[0], rtol=1e-12):
                indperm = np.argsort(dist)
            else:
                indperm = np.arange(num_points)

            s = self.point_size[np.mod(k, len(self.point_size))]
            marker = self.point_marker[np.mod(k, len(self.point_marker))]
            style = self.point_style[k]

            if self._inner_point_color[k] is not None:
                color = self._inner_point_color[k]
            elif self.point_color is not None:
                color = self.point_color
            elif style in ['s', 'l']:
                color = [self.point_default_color[k % len(self.point_default_color)]]
            elif style == 'm':
                length = np.ceil(num_points/len(self.point_default_color))
                color = np.tile(self.point_default_color, length.astype(int))
                color = color[indperm]
                color = list(color)

            if style in ['s', 'm']:
                self.axes.scatter(np.real(points[1][indperm]),
                                  -np.real(points[0][indperm]),
                                  np.real(points[2][indperm]),
                                  s=s, marker=marker, color=color,
                                  alpha=self.point_alpha[k],
                                  edgecolor=None, zdir='z')
            elif style == 'l':
                # Handle color for line style
                if isinstance(color, list) and len(color) > 0:
                    line_color = color[0] if len(color) == 1 else color[k % len(color)]
                else:
                    line_color = color
                self.axes.plot(np.real(points[1]),
                               -np.real(points[0]),
                               np.real(points[2]),
                               color=line_color,
                               alpha=self.point_alpha[k],
                               zdir='z')

    def plot_annotations(self):
        """Plot text annotations."""
        for annotation in self.annotations:
            vec = annotation['position']
            opts = {
                'fontsize': self.font_size * 0.9,  # Slightly smaller than axis labels
                'color': self.font_color,
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
                'fontfamily': self.font_family,
                'weight': 'normal'
            }
            opts.update(annotation['opts'])
            self.axes.text(vec[1], -vec[0], vec[2],
                           annotation['text'], **opts)

    def plot_lines(self):
        """Plot line segments."""
        for line, fmt, kw in self._lines:
            self.axes.plot(line[0], line[1], line[2], fmt, **kw)

    def plot_arcs(self, plot_area: Literal["rear", "inner", "front"]):
        """Plot arcs in specified area."""
        for arc, area, fmt, kw in self._arcs:
            if plot_area == area:
                self.axes.plot(arc[:, 1], -arc[:, 0], arc[:, 2], fmt, **kw)

    def run_from_ipython(self):
        """Check if running from IPython."""
        try:
            __IPYTHON__
            return True
        except NameError:
            return False

    def _is_inline_backend(self):
        """Check if using inline backend."""
        backend = matplotlib.get_backend()
        return backend == "module://matplotlib_inline.backend_inline"

    def make_sphere(self):
        """Alias for render()."""
        self.render()

    def show(self):
        """Display Bloch sphere."""
        self.render()
        if self.run_from_ipython():
            display(self.fig)
        else:
            self.fig.show()

    def save(self, name=None, format='png', dirc=None, dpin=None):
        """Save Bloch sphere to file.

        Parameters
        ----------
        name : str
            Filename (overrides format and dirc).
        format : str
            Output format.
        dirc : str
            Output directory.
        dpin : int
            Resolution in DPI.
        """
        self.render()
        
        if dirc:
            if not os.path.isdir(os.getcwd() + "/" + str(dirc)):
                os.makedirs(os.getcwd() + "/" + str(dirc))
                
        if name is None:
            if dirc:
                complete_path = os.getcwd() + "/" + str(dirc) + '/bloch_' \
                                + str(self.savenum) + '.' + format
            else:
                complete_path = os.getcwd() + '/bloch_' + \
                                str(self.savenum) + '.' + format
        else:
            complete_path = name

        if dpin:
            self.fig.savefig(complete_path, dpi=dpin)
        else:
            self.fig.savefig(complete_path)
            
        self.savenum += 1
        if self.fig:
            plt.close(self.fig)