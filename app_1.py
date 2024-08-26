

import streamlit as st
import pandas as pd
import requests
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import ast



# Load data
@st.cache_data
def load_data():
    path_to_data = 'C:/Users/janko/python/data/net_for_pyt.csv'
    return pd.read_csv(path_to_data)


df = load_data()

st.title("Netzwerkberechnung mit EMA-Daten aus der SmartVoices-Studie")

ids_not_working =(2822, 2823, 2856, 2862, 2870, 2856, 2862, 2870, 2881, 2885) #these ids did not work 

df_filtered = df[~df['user_id'].isin(ids_not_working)] #exlude them from the df

#vector with IDs that are working
testable_ids = df_filtered['user_id'].unique()

# Convert array to DataFrame for better visualization
testable_ids_df = pd.DataFrame(testable_ids, columns=['EMA-IDs'])

# Sidebar for user input
#user_id = st.sidebar.number_input('Gib deine SmartVoices-ID ein', value=9999, step=1)
st.title('Eingabe deiner persönlichen ID')
# Main content area for user input
user_id = st.number_input('Gib deine SmartVoices-ID ein und drücke auf den untenstehenden Knopf, um dein Netzwerk zu berechnen.', value=9999, step=1) #Eingabe ID

# here I want to implement a variable selection
item_selection = st.multiselect(
    "select variables for your personal network",
    ["Angespannt", "Stimmenhören", "Belastung Stimmen"],
    ["Angespannt", "Belastung Stimmen"],
)

# Mapping dictionary
mapping_dict = {
    "Angespannt": "V1",
    "Stimmenhören": "V2",
    "Belastung Stimmen": "V3",
    "Stimmen böse": "V4",
    "NSSV": "V5",
}

transformed_list = [mapping_dict[item] for item in item_selection]

st.write("You select:", item_selection)

# Button
clicked = st.button('Berechne dein persönliches Netzwerk')

# Button to trigger computation
if clicked:
    
    df_ind = df_filtered[df_filtered['user_id'] == user_id] #select user id

    if not df_ind.empty:
        
        with st.spinner('Bitte warte, während dein Netzwerk berechnet wird...'):
            #time.sleep(30)
                    
            df_ind_net = df_ind.drop(df_ind.columns[[0, 1, 2]], axis=1)

         # Assuming 'df' is your pandas DataFrame
            df_json = df_ind_net.to_json(orient='split')
            payload = json.dumps({"df_json": df_json})
            headers = {'Content-Type': 'application/json'}

            response = requests.post('http://localhost:8001/computeVAR', data=payload, headers=headers)
       
          # First, extract the actual JSON string from the list
            list_R = response.json()

            json_string = list_R[0]

            # Parse JSON string to Python list of dictionaries
            parsed_data = json.loads(json_string)

            df_final = pd.DataFrame(parsed_data)

            df_final = df_final.iloc[:, 0:5]

            df_select = df_final[transformed_list]

            array = df_select.to_numpy()

            print(df_final)

            # Create a directed graph from a numpy array
            G = nx.from_numpy_array(array, create_using=nx.DiGraph)

            # Knoten-Labels zuweisen
            #labels_network <- c("Angespannt", "Stimmenhören", "Belastung Stimmen",  "Stimmen böse","NSSV",  "Suizidgedanken")
            node_labels = {0: 'Stimmenhören', 1: 'Belastung Stimmen', 2: 'Böse Stimmen', 3: 'Selbstverletzung', 4:'Suizidgedanken'}
            nx.set_node_attributes(G, node_labels, 'label')

            # Remove edges with weight 0
            edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d.get('weight', 1) == 0]
            G.remove_edges_from(edges_to_remove)
            
            # Compute positions for the nodes using a fixed seed and circular layout for uniform edge length
            pos = nx.circular_layout(G)

            # Compute positions for the nodes using spring layout with a specific 'k' value
            #pos = nx.spring_layout(G, k=0.15)  # Play with this value to adjust distances

            # Retrieve edges and their weights
            edges = G.edges(data=True)
            weights = [d['weight'] for u, v, d in edges]

            # Create a matplotlib figure
            fig, ax = plt.subplots(figsize=(7, 7))

            # Draw the network graph
            nx.draw(G, pos, with_labels=False, node_size=4000, edge_color=weights,
            edge_cmap=plt.cm.Blues, width=5, ax=ax)

            # Draw edge labels with weights
            edge_labels = nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f"{d['weight']:.3f}" for u, v, d in edges}, ax=ax)

            # Set the title of the plot
            ax.set_title('Visualisierung der Zusammenhänge zwischen deinen Symptomen')
            
            # Zeichne die Knoten-Labels basierend auf den benutzerdefinierten Labels
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=6, font_color='white')

            # Set aspect of the plot to 'equal' to maintain the scale of x and y axes
            ax = plt.gca()
            ax.set_aspect('equal')

            # Dynamically adjust axes limits based on positions
            x_values, y_values = zip(*pos.values())
            x_min, x_max = min(x_values), max(x_values)
            y_min, y_max = min(y_values), max(y_values)
            ax.set_xlim(x_min - 0.5, x_max + 0.5)
            ax.set_ylim(y_min - 0.5, y_max + 0.5)

            # Add margins and use tight layout to ensure all labels and nodes fit within the plot
            #plt.margins(0.1)
            plt.tight_layout()

            # Display the plot in Streamlit
            #st.balloons()
            st.pyplot(fig)
            
    else:
        st.error("Für diese ID sind keine Daten verfügbar.")
else:
    st.write("Achtung: Die Berechnung kann eine Weile dauern.")


# Button to show testable IDs
if st.button('Zeige verfügbare SmartVoices-IDs'):
    st.write("Verfügbare IDs:")
    st.table(testable_ids_df)
    
else:
    st.write("Drücke den Knopf, um die für die Testung verwendbaren IDs anzuzeigen.")

#to make it accessible in local network:
#find ip with: Using Command Prompt:
#Open Command Prompt by typing cmd in the search bar and opening the application.
#Type ipconfig and press Enter.
#Look for the "IPv4 Address" under your network connection (this is your local IP address).
#streamlit run app_1.py --server.address="0.0.0.0" --server.port=8501 --> in powershell: But it probably isnt even necessary
#then type in browser: http://130.92.159.42:8501/ 
