import os
import glob
import numpy as np

from DataVisualizationEditingTool.utils.data_loader import DataLoader
from DataVisualizationEditingTool.utils.data_manager import DataManager


def main():
    """
    Loads lane data from the 'lanes' directory and returns it.
    This function is now designed to be imported and used by other scripts.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lanes_path = os.path.join(script_dir, 'lanes')

    if not os.path.isdir(lanes_path):
        return np.array([]), np.array([]), []

    # Dynamically load all .npy files from the 'lanes' directory
    file_paths = glob.glob(os.path.join(lanes_path, 'lane-*.npy'))
    if not file_paths:
        return np.array([]), np.array([]), []

    # Extract file names for the loader
    file_names = [os.path.basename(p) for p in file_paths]

    loader = DataLoader(lanes_path, file_order=file_names)
    nodes, edges, loaded_file_names = loader.load_data()

    if nodes.size == 0:
        return np.array([]), np.array([]), []

    return nodes, edges, loaded_file_names


if __name__ == "__main__":
    nodes, edges, file_names = main()
    if nodes.size > 0:
        print(f"Loaded {len(file_names)} files.")
        print(f"Total nodes: {nodes.shape[0]}")
        print(f"Total edges: {edges.shape[0]}")
        print(f"Unique lane IDs: {np.unique(nodes[:, 4])}")
    else:
        print("No data loaded.")
