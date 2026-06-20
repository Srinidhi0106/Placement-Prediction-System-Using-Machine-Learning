import matplotlib
matplotlib.use('Agg')   # IMPORTANT for Flask

import matplotlib.pyplot as plt
import os

def generate_graph():

    features = ['CGPA', 'Attendance', 'Internships',
                'Technical Skills', 'Communication Skills', 'Backlogs']

    importance = [0.26, 0.05, 0.03, 0.21, 0.22, 0.23]

    plt.figure(figsize=(8,5))
    plt.bar(features, importance)
    plt.title("Feature Importance for Placement")
    plt.xticks(rotation=30)
    plt.tight_layout()

    # Save image inside static folder
    graph_path = os.path.join('static', 'placement_graph.png')
    plt.savefig(graph_path)
    plt.close()

    return 'placement_graph.png'    