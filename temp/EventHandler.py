class EventHandler:
    def __init__(self):
        self.plot_manager = None
        self.current_mode = 'selection'
        self.smoothing_active = False

    def set_plot_manager(self, plot_manager):
        self.plot_manager = plot_manager
        self.plot_manager.event_handler = self
        self.setup_event_handlers()
        self.update_ui_state()

    def setup_event_handlers(self):
        # Basic click and key events for demonstration
        self.plot_manager.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.plot_manager.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def update_ui_state(self):
        # Call PlotManager's method to update button visibility and highlights
        self.plot_manager.update_button_states(self.current_mode, self.smoothing_active)
        self.plot_manager.update_status(f"Mode: {self.current_mode.capitalize()}")

    def on_button_click(self, button_key):
        print(f"Button '{button_key}' clicked (dummy action)")
        self.plot_manager.update_status(f"'{button_key}' clicked.")

        # Logic to change modes
        if button_key == 'select_mode':
            self.current_mode = 'selection'
            self.smoothing_active = False  # Reset smoothing state
            self.plot_manager.rs.set_active(True)  # Activate rectangle selector
        elif button_key == 'draw_mode':
            self.current_mode = 'draw'
            self.smoothing_active = False
            self.plot_manager.rs.set_active(False)
        elif button_key == 'add_delete_mode':
            self.current_mode = 'add_delete'
            self.smoothing_active = False
            self.plot_manager.rs.set_active(False)
        elif button_key == 'straighten':  # Smooth Selected
            if self.current_mode == 'selection':
                self.smoothing_active = True
                self.plot_manager.update_status("Click plot for Smoothing Start Point")
        elif button_key == 'cancel_smoothing':
            self.smoothing_active = False
            self.plot_manager.update_status("Smoothing canceled.")
        elif button_key == 'toggle_grid':
            self.plot_manager.grid_visible = not self.plot_manager.grid_visible
            self.plot_manager.ax.grid(self.plot_manager.grid_visible)
            self.plot_manager.update_status(f"Grid {'enabled' if self.plot_manager.grid_visible else 'disabled'}")
            self.plot_manager.fig.canvas.draw_idle()

        self.update_ui_state()  # Update UI after mode change

    def on_slider_change(self, slider_name):
        def _handler(val):
            print(f"Slider '{slider_name}' value changed to: {val:.2f} (dummy action)")
            self.plot_manager.update_status(f"{slider_name}: {val:.2f}")
            # For point size, we can actually update the dummy plot
            if slider_name == 'Point Size':
                self.plot_manager.update_plot(self.plot_manager.data)  # Redraw plot with new size

        return _handler

    def on_click(self, event):
        if event.inaxes != self.plot_manager.ax: return
        print(f"Plot clicked at ({event.xdata:.2f}, {event.ydata:.2f}) with button {event.button}")
        self.plot_manager.update_status(f"Plot clicked at ({event.xdata:.2f}, {event.ydata:.2f})")

        if self.smoothing_active:
            if event.button == 1:  # Left click for point selection
                print(f"Selected point for smoothing at ({event.xdata:.2f}, {event.ydata:.2f})")
                self.plot_manager.update_status(f"Smoothing point selected: ({event.xdata:.2f}, {event.ydata:.2f})")

        # Dummy draw mode interaction
        if self.current_mode == 'draw':
            if event.button == 1:
                # Add dummy points for current_line visualization
                if not hasattr(self.plot_manager, 'dummy_draw_line'):
                    self.plot_manager.dummy_draw_line = self.plot_manager.ax.plot([], [], 'k-', alpha=0.5)[0]
                    self.plot_manager.dummy_draw_points = []
                self.plot_manager.dummy_draw_points.append([event.xdata, event.ydata])
                x, y = zip(*self.plot_manager.dummy_draw_points)
                self.plot_manager.dummy_draw_line.set_data(x, y)
                self.plot_manager.fig.canvas.draw_idle()
                print("Dummy draw point added.")
            elif event.button == 3:  # Right click to clear dummy draw line
                if hasattr(self.plot_manager, 'dummy_draw_line') and self.plot_manager.dummy_draw_line:
                    self.plot_manager.dummy_draw_line.remove()
                    del self.plot_manager.dummy_draw_line
                    del self.plot_manager.dummy_draw_points
                    self.plot_manager.fig.canvas.draw_idle()
                    print("Dummy draw line cleared.")
            self.plot_manager.update_status("Drawing...")

    def on_key(self, event):
        print(f"Key '{event.key}' pressed (dummy action)")
        self.plot_manager.update_status(f"Key '{event.key}' pressed.")

    def on_select(self, eclick, erelease):
        # This is for the RectangleSelector. Just print coordinates.
        if self.current_mode == 'selection':
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            print(f"Selection box from ({x1:.2f},{y1:.2f}) to ({x2:.2f},{y2:.2f}) (dummy action)")
            self.plot_manager.update_status(f"Selected area: ({x1:.1f},{y1:.1f}) to ({x2:.1f},{y2:.1f})")

    # Dummy methods for functionalities not implemented in UI preview
    def update_point_sizes(self, val):
        print(f"Dummy: Update point sizes to {val}")
        # In the real app, this would iterate scatter plots and set sizes.
        # For this dummy, the plot is redrawn via slider_point_size.on_changed
        # which calls on_slider_change which then calls update_plot.

    def update_smoothing_weight(self, val):
        print(f"Dummy: Update smoothing weight to {val}")

    def update_smoothness(self, val):
        print(f"Dummy: Update smoothness to {val}")
