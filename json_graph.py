import json
import heapq
import numpy as np
from math import radians, cos, sin, asin, sqrt
from collections import deque
import pandas as pd

class abstract_graph:
    
    def __init__(self,_edges):
        self.edges=_edges
        self.nodes={u for u,v in self.edges} | {v for u,v in self.edges}
    
    def adjacency_list(self):
        pass

    def depth_first(self, start):
        path, stack = [], deque()
        stack.append(start)
        L = self.adjacency_list()
        while stack:
            vertex = stack.pop()
            if vertex not in path:
                path.append(vertex)
                stack.extend(L[vertex] - set(path))
        return path

    def breadth_first(self, start):
        path, queue = [], deque()
        queue.append(start)
        L = self.adjacency_list()
        while queue:
            vertex = queue.popleft()
            if vertex not in path:
                path.append(vertex)
                queue.extend(L[vertex] - set(path))
        return path
        
class simple_graph(abstract_graph):
    
    def adjacency_matrix(self):
        n=len(self.nodes)
        mat=np.zeros((n,n))
        for i,v in enumerate(self.nodes):
            for j,k in enumerate(self.nodes):
                if (v,k) in self.edges:
                    mat[i,j]=1
                    mat[j,i]=1
        return mat
    
    def adjacency_list(self):
        adjacent=lambda n : {v for u,v in self.edges if u==n } | {u for u,v in self.edges if v==n}
        return {v:adjacent(v) for v in self.nodes}

class simple_digraph(abstract_graph):
    
    def __init__(self,_edges):
        self.edges=_edges
        self.nodes={u for u,v in self.edges if u!=None} | {v for u,v in self.edges if v!=None}
        
    def adjacency_matrix(self):
        n=len(self.nodes)
        mat=np.zeros((n,n))
        for i,v in enumerate(self.nodes):
            for j,k in enumerate(self.nodes):
                if (v,k) in self.edges:
                    mat[i,j]=1
        return mat

    def adjacency_list(self):
        adjacent=lambda n : {v for u,v in self.edges if u==n and v!=None} 
        return {v:adjacent(v) for v in self.nodes} 
    
    def in_degree(self):
        degree= lambda n : len({u for u,v in self.edges if v==n and u!=None})
        return {v:degree(v) for v in self.nodes}
        
    def google_matrix(self,alpha=0.85):
        n=len(self.nodes)
        E=np.ones((n,n))/float(n)
        A=self.adjacency_matrix()
        row_sums = A.sum(axis=1)
        A[row_sums==0,:]=1/float(n)
        row_sums[row_sums==0]=1
        W = A / row_sums[:, np.newaxis]
        W_star=alpha*W+(1-alpha)*E
        return W_star

class weighted_graph(simple_graph):
    
    def __init__(self,_edges):
        self.edges=_edges
        self.nodes={u for u,v in self.edges.keys()} | {v for u,v in self.edges.keys()}
    
    def adjacency_list(self):
        adjacent=lambda n : {v for u,v in self.edges.keys() if u==n } | {u for u,v in self.edges.keys() if v==n}
        return {v:adjacent(v) for v in self.nodes}

    def dijkstra(self,start,weight):
        L = self.adjacency_list()
        U = {start:start}
        D = {v:float('inf') for v in self.nodes}
        D.update({start:0})
        PQ = []
        heapq.heappush(PQ,(start,0))
        for neighbor in L[start]:
            if (start,neighbor) in self.edges:
                cost=self.edges[(start,neighbor)][weight]
            else:
                cost=self.edges[(neighbor,start)][weight]
            heapq.heappush(PQ,(neighbor,cost))
        while len(PQ)>0:
            node,node_cost=heapq.heappop(PQ)
            for neighbor in L[node]:
                if (node,neighbor) in self.edges:
                    cost=node_cost+self.edges[(node,neighbor)][weight]
                else:
                    cost=node_cost+self.edges[(neighbor,node)][weight]
                if D[neighbor]>(cost):
                    D.update({neighbor:cost})
                    heapq.heappush(PQ,(neighbor,cost))
                    U.update({neighbor:node})
        return D,U

    def shortest_path(self,parent,start,end):
        path=[end]
        k=end
        while k!=start:
            path.append(parent[k])
            k=parent[k]
        return path
        
class json_graph(weighted_graph):

    def __init__(self,_path):
        with open(_path) as file:
            self.data=json.load(file)
        self.edges=dict()
        self.nodes=dict()
        for i in range(len(self.data['features'])):
            source=int(self.data['features'][i]['properties']['from'])
            target=int(self.data['features'][i]['properties']['to'])
            length=float(self.data['features'][i]['properties']['length'])
            name=str(self.data['features'][i]['properties']['name'])
            maxspeed=str(self.data['features'][i]['properties']['maxspeed'])
            self.edges.update({(source,target):{'largo':length,'maxvel':maxspeed,'nombre':name}})
            self.nodes.update({source:self.data['features'][i]['geometry']['coordinates'][0]})
            self.nodes.update({target:self.data['features'][i]['geometry']['coordinates'][1]})
        
        
    def draw_graph(self):
        geo_json=[]
        for e in self.data['features']:
            if 'geometry' in e:
                line_string = {
                    'type': 'Feature',
                    'properties':{
                        'length':e['properties']['length'],
                        'source':e['properties']['from'],
                        'target':e['properties']['to']
                    },
                    'geometry':{
                        'type':'LineString',
                        'coordinates': e['geometry']['coordinates']
                    }   
                }
                geo_json.append(line_string)
        geometries = {
            'type': 'FeatureCollection',
            'features': geo_json,
        }
        geo_str = json.dumps(geometries)
        return geo_str



