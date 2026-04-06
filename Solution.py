from Traversals import bfs_path
import heapq
from collections import deque
from Simulator import Simulator
import sys

class Solution:
    def __init__(self, problem, isp, graph, info):
        self.problem = problem
        self.isp = isp
        self.graph = graph
        self.info = info

    def output_paths(self):
        paths, bandwidths, priorities = {}, {}, {}

        list_clients = self.info["list_clients"]
        payments = self.info["payments"]
        bws = self.info["bandwidths"]

        def get_payment_amount(client):
            return payments.get(client, 0)
        
        paying_clients = [c for c in list_clients if get_payment_amount(c) > 0]
        sorted_clients = sorted(paying_clients, key=get_payment_amount, reverse=True)

        base_paths = bfs_path(self.graph, self.isp, list_clients)

        node_usage = {node: 0 for node in self.graph}

        penalty_mult = {}
        for v, b in bws.items():
            if b > 0 and b != float('inf'):
                penalty_mult[v] = 2.5 / b

        for client in sorted_clients:
            fast_path = base_paths.get(client, [])
            is_congested = False

            for node in fast_path:
                b = bws.get(node, float('inf'))
                if b != float('inf') and b > 0:
                    if node_usage[node] >= b:
                        is_congested = True
                        break

            if not is_congested and fast_path:
                paths[client] = fast_path
                for node in fast_path:
                    node_usage[node] += 1
                continue
            
            pq = [(0, self.isp)]
            dist = {self.isp: 0}
            parent = {self.isp: None}

            while pq:
                d, u = heapq.heappop(pq)

                if d > dist.get(u, float('inf')):
                    continue

                if u == client:
                    break

                for v in self.graph[u]:
                    cost_v = 1
                    
                    if v in penalty_mult:
                        cost_v += node_usage[v] * penalty_mult[v]

                    new_dist = d + cost_v
                    if new_dist < dist.get(v, float('inf')):
                        dist[v] = new_dist
                        parent[v] = u
                        heapq.heappush(pq, (new_dist, v))

            path = []
            curr = client
            while curr is not None:
                path.append(curr)
                curr = parent.get(curr)
            
            path.reverse()
            paths[client] = path

            for node in path:
                node_usage[node] += 1

        return (paths, bandwidths, priorities)