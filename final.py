import networkx as nx
import json
import pandas as pd
import numpy as np
import json_graph as jgraph
import geocoder
from scipy.spatial import KDTree
import time

def load_node_data(graph):    
    df=pd.DataFrame.from_dict(graph.nodes, orient='index',columns=['lon','lat'])
    return df

def load_edge_data(graph):    
    df=pd.DataFrame.from_dict(graph.edges, orient='index')
    return df

def create_graph(DATA_PATH):
    return jgraph.json_graph(DATA_PATH)

def create_tree(DATA_PATH):
    return KDTree(node_data.values)

def geocode(address):
    address=address+", Talca CL"
    res=geocoder.osm(address)
    return res.ok,res.geojson

def nearest_node(coords,node_data,tree,address_data):
    d,i=tree.query(coords)
    point=node_data.iloc[i]
    return point

def init_dest(initial, destiny):
    init_point= None
    dest_point= None

    if initial:
        ret,address_data=geocode(initial)
        if ret:
            coords=address_data['features'][0]['geometry']['coordinates']
            init_point=nearest_node(coords,node_data,tree,address_data)
            print(initial + " - lat: " + str(init_point.lat) + " lon: " + str(init_point.lon))
        else:
            init_point = True
            print('Localizacion no encontrada')

    if destiny:
        ret,address_data=geocode(destiny)
        if ret:
            coords=address_data['features'][0]['geometry']['coordinates']
            dest_point=nearest_node(coords,node_data,tree,address_data)
            print(destiny + " - lat: " + str(dest_point.lat) + " lon: " + str(dest_point.lon))
        else:
            dest_point = True
            print('Localizacion no encontrada')
            
    return init_point, dest_point

if __name__ == "__main__":
    G = nx.Graph()
    edges=dict()
    nodes=dict()

    with open('talca_ciclovias.geojson') as file:
        data=json.load(file)
    for i in range(len(data['features'])):
        source=int(data['features'][i]['properties']['from'])
        target=int(data['features'][i]['properties']['to'])
        length=float(data['features'][i]['properties']['length'])
        name=str(data['features'][i]['properties']['name'])
        G.add_edge(source, target, weight=length)
        G.add_node(source, pos=data['features'][i]['geometry']['coordinates'][0])
        G.add_node(target, pos=data['features'][i]['geometry']['coordinates'][1])

    #print(G.edges.data())
    #print(G.nodes.data())

    DATA_PATH = 'talca_ciclovias.geojson'
    graph=create_graph(DATA_PATH)
    node_data = load_node_data(graph)
    tree=create_tree(node_data)

    list_start_end = list()
    list_init = list()
    list_dest = list()

    list_start_end.append(("K-611","3 Oriente 1432"))
    list_start_end.append(("Pasaje Colbun 339", "Avenida Colin 0240"))
    list_start_end.append(("17 norte 3275", "K-611"))
    list_start_end.append(("Pasaje 15 1/2 Sur 1859", "17 norte 3275"))

    for i in list_start_end:
        init_point, dest_point = init_dest(i[0], i[1])
        list_init.append(init_point)
        list_dest.append(dest_point)
        print("--------------------------")

    for j,k in zip(list_init, list_dest):
        print("Origen: " + str(j.name),'\t', "Destino: " + str(k.name))

        if not j is None and not k is None:
            start_time = time.time()
            print("Distancia Dijkstra: " + str(nx.dijkstra_path_length(G, j.name, k.name, weight='weight')))
            print("--- %s segundos ---" % (time.time() - start_time))


            start_time = time.time()
            print("Distancia Bellman Ford: " + str(nx.bellman_ford_path_length(G, j.name, k.name, weight='weight')))
            print("--- %s segundos ---" % (time.time() - start_time))
        print("-----------------------------")
