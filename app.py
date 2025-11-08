from flask import Flask, jsonify, render_template
import numpy as np

# These imports will need to be adjusted based on the refactored project structure
from DataVisualizationEditingTool.main import main as load_data_func
from DataVisualizationEditingTool.utils.data_loader import DataLoader
from DataVisualizationEditingTool.utils.data_manager import DataManager

app = Flask(__name__, template_folder='DataVisualizationEditingTool/templates', static_folder='DataVisualizationEditingTool/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    try:
        nodes, edges, _ = load_data_func()

        # Convert numpy arrays to lists for JSON serialization
        nodes_list = nodes.tolist() if isinstance(nodes, np.ndarray) else nodes
        edges_list = edges.tolist() if isinstance(edges, np.ndarray) else edges

        return jsonify({
            'nodes': nodes_list,
            'edges': edges_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
