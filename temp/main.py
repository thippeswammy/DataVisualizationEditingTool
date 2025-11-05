import matplotlib.pyplot as plt
from DataVisualizationEditingTool.temp.PlotManager import PlotManager
from DataVisualizationEditingTool.temp.EventHandler import EventHandler

if __name__ == "__main__":
    event_handler = EventHandler()
    plot_manager = PlotManager(event_handler) # Pass event_handler to plot_manager
    event_handler.set_plot_manager(plot_manager) # Pass plot_manager back to event_handler

    plt.show()