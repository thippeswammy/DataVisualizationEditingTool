# dummy_plot_manager.py

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button, RectangleSelector

class PlotManager:
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.fig, self.ax = plt.subplots(figsize=(12, 8))

        # Dummy data for plotting
        self.data = np.array([[0, 0, 0, 0, 0, 0], [10, 10, 0, 1, 1, 0], [20, 5, 0, 2, 2, 1], [30, 15, 0, 3, 3, 1]])
        self.file_names = {0: "Dummy_Lane_0.npy", 1: "Dummy_Lane_1.npy"}

        # Store button objects for visibility toggling
        self.buttons = {}
        # Store slider objects
        self.slider_point_size = None
        self.slider_smoothness = None
        self.slider_base_weight = None

        self.rs = RectangleSelector(self.ax, self.event_handler.on_select, useblit=True, button=[1])
        self.rs.set_active(False) # Start inactive

        # Keep track of plot elements we want to clear
        self.lane_scatter_plots = []
        self.start_point_plots = []
        self.extra_scatter_plots = [] # For selected points, merge points, etc.
        self.tooltip_text_artist = None # To manage the tooltip text artist
        self.nearest_point_artist = None # To manage the nearest point highlight

        self.setup_widgets()
        self.setup_navigation() # Keep scroll/motion for basic interaction
        self.update_plot(self.data) # Initial plot update

    def setup_widgets(self):
        # ... (rest of setup_widgets remains the same)
        # Define common button/slider dimensions and spacing
        btn_width = 0.08
        btn_height = 0.04
        btn_spacing_x = 0.09
        btn_spacing_y = 0.01

        #  Top Global Toolbar Buttons 
        top_row_y = 0.95
        self.buttons['undo'] = Button(plt.axes([0.01, top_row_y, btn_width, btn_height]), 'Undo')
        self.buttons['redo'] = Button(plt.axes([0.01 + btn_spacing_x, top_row_y, btn_width, btn_height]), 'Redo')
        self.buttons['save'] = Button(plt.axes([0.01 + 2 * btn_spacing_x, top_row_y, btn_width, btn_height]), 'Save')
        self.buttons['export'] = Button(plt.axes([0.01 + 3 * btn_spacing_x, top_row_y, btn_width, btn_height]), 'Export Selected')
        self.buttons['grid'] = Button(plt.axes([0.01 + 4 * btn_spacing_x, top_row_y, btn_width, btn_height]), 'Toggle Grid')

        #  Mode Selection Buttons 
        mode_btn_y = 0.88
        mode_btn_width = 0.12
        mode_btn_spacing_x = 0.13

        self.buttons['select_mode'] = Button(plt.axes([0.01, mode_btn_y, mode_btn_width, btn_height]), 'Select Mode')
        self.buttons['draw_mode'] = Button(plt.axes([0.01 + mode_btn_spacing_x, mode_btn_y, mode_btn_width, btn_height]), 'Draw Mode')
        self.buttons['add_delete_mode'] = Button(plt.axes([0.01 + 2 * mode_btn_spacing_x, mode_btn_y, mode_btn_width, btn_height]), 'Add/Delete Mode')

        #  Right Sidebar Sliders (Global Settings) 
        slider_left = 0.85
        slider_width = 0.12
        slider_height = 0.03
        slider_spacing_y = 0.05

        self.slider_point_size = Slider(plt.axes([slider_left, 0.10, slider_width, slider_height]), 'Point Size', 1, 100, valinit=10)
        self.slider_smoothness = Slider(plt.axes([slider_left, 0.10 + slider_spacing_y, slider_width, slider_height]), 'Smoothness', 0.1, 30.0, valinit=1.0)
        self.slider_base_weight = Slider(plt.axes([slider_left, 0.10 + 2 * slider_spacing_y, slider_width, slider_height]), 'Base Weight', 1, 100, valinit=20)

        #  Right Sidebar Buttons (Mode-Specific / Contextual) 
        sidebar_btn_y_start = 0.75 # Adjust based on how much space you want above sliders
        sidebar_btn_spacing_y = 0.05 # Spacing between these buttons

        # Draw Mode Controls
        self.buttons['linecurve'] = Button(plt.axes([slider_left, sidebar_btn_y_start, slider_width, btn_height]), 'Line')
        self.buttons['finalize_draw'] = Button(plt.axes([slider_left, sidebar_btn_y_start - sidebar_btn_spacing_y, slider_width, btn_height]), 'Finalize Draw (Enter)')

        # Select Mode Controls (Smoothing)
        self.buttons['straighten'] = Button(plt.axes([slider_left, sidebar_btn_y_start, slider_width, btn_height]), 'Smooth Selected')
        self.buttons['confirm_start'] = Button(plt.axes([slider_left, sidebar_btn_y_start - sidebar_btn_spacing_y, slider_width, btn_height]), 'Confirm Start')
        self.buttons['confirm_end'] = Button(plt.axes([slider_left, sidebar_btn_y_start - 2*sidebar_btn_spacing_y, slider_width, btn_height]), 'Confirm End')
        self.buttons['cancel_smoothing'] = Button(plt.axes([slider_left, sidebar_btn_y_start - 3*sidebar_btn_spacing_y, slider_width, btn_height]), 'Cancel Smoothing')

        # General Action Buttons (bottom of sidebar)
        self.buttons['cancel_operation'] = Button(plt.axes([slider_left, 0.05, slider_width, btn_height]), 'Cancel Operation')
        self.buttons['clear_selection'] = Button(plt.axes([slider_left, 0.01, slider_width, btn_height]), 'Clear Selection')


        # Connect button click events (to dummy handlers)
        for key, button in self.buttons.items():
            button.on_clicked(lambda event, k=key: self.event_handler.on_button_click(k))

        # Connect slider change events (to dummy handlers)
        self.slider_point_size.on_changed(self.event_handler.on_slider_change('Point Size'))
        self.slider_smoothness.on_changed(self.event_handler.on_slider_change('Smoothness'))
        self.slider_base_weight.on_changed(self.event_handler.on_slider_change('Base Weight'))


        self.fig.canvas.draw()


    def setup_navigation(self):
        # Connect basic navigation events (scroll, motion)
        """Connect basic navigation events to the figure canvas."""
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        # self.fig.canvas.mpl_connect('pick_event', self.on_legend_pick) # Legend pick requires data.
        self.ax.set_navigate(True)

    def on_scroll(self, event):
        """Adjusts the x and y limits of the axes based on scroll events."""
        if event.inaxes != self.ax: return
        base_scale = 1.1
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if event.button == 'up': scale = 1 / base_scale
        elif event.button == 'down': scale = base_scale
        else: return
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale
        self.ax.set_xlim([xdata - new_width * (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0]),
                          xdata + new_width * (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])])
        self.ax.set_ylim([ydata - new_height * (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0]),
                          ydata + new_height * (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])])
        self.fig.canvas.draw_idle()

    def on_motion(self, event):
        # Dummy motion handler, no actual point data lookup
        """Handles motion events for the figure canvas."""
        if event.inaxes != self.ax:
            # Removed tooltip and nearest_point management here as they are not defined in this dummy.
            self.fig.canvas.draw_idle()
            return
        self.fig.canvas.draw_idle()

    def update_plot(self, data):
        # Clear only the plot elements that are part of the data visualization
        # Do NOT attempt to remove Axes objects associated with widgets (buttons, sliders)
        """Update the plot with new data and clear previous elements.
        
        This function clears existing plot elements related to the data visualization,
        including scatter plots and any dummy lines from drawing mode. It then checks
        if new data is provided, and if so, it plots the unique lane data with
        appropriate colors and labels. If no data is available, a message indicating
        the absence of data is displayed. The axes labels and title are also set
        accordingly, and the plot is refreshed.
        
        Args:
            data: A numpy array containing the data to be visualized.
        """
        for plot_element in self.lane_scatter_plots + self.start_point_plots + self.extra_scatter_plots:
            if plot_element in self.ax.collections: # Check if it's still on the axes
                plot_element.remove()
        self.lane_scatter_plots = []
        self.start_point_plots = []
        self.extra_scatter_plots = []

        # Also clear any dummy lines from drawing mode
        if hasattr(self, 'dummy_draw_line') and self.dummy_draw_line in self.ax.lines:
            self.dummy_draw_line.remove()
            del self.dummy_draw_line
            del self.dummy_draw_points
        # self.ax.lines = [line for line in self.ax.lines if line.get_label() != 'Preview'] # Remove preview line if it exists

        # Plot dummy data
        if data.size > 0:
            unique_lane_ids = np.unique(data[:, -1])
            colors = plt.cm.get_cmap('tab10')(np.linspace(0, 1, max(len(unique_lane_ids), 10)))

            for lane_id in unique_lane_ids:
                mask = data[:, -1] == lane_id
                lane_data = data[mask]
                if len(lane_data) > 0:
                    label = self.file_names.get(int(lane_id), f"Lane {int(lane_id)}")
                    point_size = self.slider_point_size.val if self.slider_point_size else 10
                    sc = self.ax.scatter(lane_data[:, 0], lane_data[:, 1], s=point_size,
                                         label=label, color=colors[int(lane_id)], marker='o')
                    self.lane_scatter_plots.append(sc) # Store the new scatter plot
        else:
            self.ax.text(0.5, 0.5, "No Dummy Data", transform=self.ax.transAxes,
                         ha='center', va='center', fontsize=20, color='gray')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Lane Data Visualization (UI Preview)')
        self.ax.grid(False) # Start with grid off
        self.ax.legend()
        self.fig.canvas.draw_idle()

    def update_status(self, message=""):
        # This will update the main plot title to show status messages
        self.ax.set_title(f'Lane Data Visualization (UI Preview): {message}' if message else 'Lane Data Visualization (UI Preview)')
        self.fig.canvas.draw_idle()

    def update_button_states(self, current_mode, smoothing_active=False):
        # ... (This method remains the same as in the previous response's `dummy_plot_manager.py`)
        # Helper to set button visibility based on current mode
        """Update the visibility and state of buttons based on the current mode.
        
        This method manages the visibility and interactivity of various buttons  in the
        user interface according to the specified `current_mode`. It ensures  that
        global toolbar buttons are always visible, highlights the active mode  button,
        and adjusts the visibility of contextual buttons based on the  current mode and
        whether smoothing is active. The function also updates  slider visibility and
        triggers a redraw of the figure canvas.
        
        Args:
            current_mode (str): The current mode of the application, which can be
                'selection', 'draw', or 'add_delete'.
            smoothing_active (bool?): Indicates if the smoothing process
                is currently active. Defaults to False.
        """
        for key, btn in self.buttons.items():
            btn.ax.set_visible(False)
            btn.eventson = False

        # Global toolbar always visible
        self.buttons['undo'].ax.set_visible(True); self.buttons['undo'].eventson = True
        self.buttons['redo'].ax.set_visible(True); self.buttons['redo'].eventson = True
        self.buttons['save'].ax.set_visible(True); self.buttons['save'].eventson = True
        self.buttons['export'].ax.set_visible(True); self.buttons['export'].eventson = True # Assume export is always enabled for dummy
        self.buttons['grid'].ax.set_visible(True); self.buttons['grid'].eventson = True
        self.buttons['clear_selection'].ax.set_visible(True); self.buttons['clear_selection'].eventson = True
        self.buttons['cancel_operation'].ax.set_visible(True); self.buttons['cancel_operation'].eventson = True

        # Mode selection buttons always visible, highlight active one
        self.buttons['select_mode'].ax.set_visible(True); self.buttons['select_mode'].eventson = True
        self.buttons['draw_mode'].ax.set_visible(True); self.buttons['draw_mode'].eventson = True
        self.buttons['add_delete_mode'].ax.set_visible(True); self.buttons['add_delete_mode'].eventson = True

        # Highlight active mode button
        self.buttons['select_mode'].ax.set_facecolor('lightcoral' if current_mode == 'selection' else 'lightgray')
        self.buttons['draw_mode'].ax.set_facecolor('lightcoral' if current_mode == 'draw' else 'lightgray')
        self.buttons['add_delete_mode'].ax.set_facecolor('lightcoral' if current_mode == 'add_delete' else 'lightgray')

        # Sliders always visible
        self.slider_point_size.ax.set_visible(True)
        self.slider_smoothness.ax.set_visible(True)
        self.slider_base_weight.ax.set_visible(True)

        # Contextual buttons
        if current_mode == 'draw':
            self.buttons['linecurve'].ax.set_visible(True); self.buttons['linecurve'].eventson = True
            self.buttons['finalize_draw'].ax.set_visible(True); self.buttons['finalize_draw'].eventson = True
        elif current_mode == 'selection':
            if not smoothing_active:
                self.buttons['straighten'].ax.set_visible(True); self.buttons['straighten'].eventson = True
            else: # Smoothing process active
                self.buttons['confirm_start'].ax.set_visible(True); self.buttons['confirm_start'].eventson = True
                self.buttons['confirm_end'].ax.set_visible(True); self.buttons['confirm_end'].eventson = True
                self.buttons['cancel_smoothing'].ax.set_visible(True); self.buttons['cancel_smoothing'].eventson = True
        # add_delete mode has no specific buttons in the sidebar

        self.fig.canvas.draw_idle()