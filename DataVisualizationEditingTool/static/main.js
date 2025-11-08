document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching data:', data.error);
                return;
            }

            const nodes = data.nodes;
            const edges = data.edges;

            // Prepare data for Plotly
            const node_traces = {};
            nodes.forEach(node => {
                const lane_id = node[4];
                if (!node_traces[lane_id]) {
                    node_traces[lane_id] = {
                        x: [],
                        y: [],
                        mode: 'markers',
                        type: 'scatter',
                        name: `Lane ${lane_id}`
                    };
                }
                node_traces[lane_id].x.push(node[1]);
                node_traces[lane_id].y.push(node[2]);
            });

            const edge_shapes = [];
            const node_coords = {};
            nodes.forEach(node => {
                node_coords[node[0]] = { x: node[1], y: node[2] };
            });

            edges.forEach(edge => {
                const from_node = node_coords[edge[0]];
                const to_node = node_coords[edge[1]];
                if (from_node && to_node) {
                    edge_shapes.push({
                        type: 'line',
                        x0: from_node.x,
                        y0: from_node.y,
                        x1: to_node.x,
                        y1: to_node.y,
                        line: {
                            color: 'grey',
                            width: 1
                        }
                    });
                }
            });

            const layout = {
                title: 'Data Visualization',
                xaxis: { title: 'X' },
                yaxis: { title: 'Y' },
                shapes: edge_shapes,
                hovermode: 'closest'
            };

            Plotly.newPlot('plot', Object.values(node_traces), layout);
        })
        .catch(error => console.error('Error fetching data:', error));
});
