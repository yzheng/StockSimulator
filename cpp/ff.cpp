#include <iostream>
#include <limits.h>
#include <string.h>
#include <queue>

using namespace std;
class GraphNode {
public:
    int capacity;
    int flow;
    int residual;
    int cost;
    GraphNode(int capacity, int flow, int residual, int cost):
      capacity(capacity), flow(flow), residual(residual), cost(cost){}
    GraphNode():
      capacity(0), flow(0), residual(0), cost(0){}
};

const int INF=100000000;

void bfsTraverse(vector<vector<GraphNode> > & graph, 
                 void( *nodeProcessor)(vector<vector<GraphNode> >& graph, int u, int v)
                ){
    int V = graph.size();
    bool visited[V];
    memset(visited, 0, sizeof(visited));

    queue<int> q;
    q.push(0);
    visited[0] = true;
    while (!q.empty()){
        int u = q.front();
        q.pop();
        for (int v = 0; v < V; v++) {
            if (visited[v] == false) {
                q.push(v);
                nodeProcessor(graph, u, v);
                visited[v] = true;
            }
        }
    }
    return;
}


bool findAugmentedPath_bfs(vector<vector<GraphNode> >& graph, int s, int t, int parent[]){

    int V = graph.size();
    bool visited[V];
    memset(visited, 0, sizeof(visited));

    queue<int> q;
    q.push(s);
    visited[s] = true;
    parent[s] = -1;

    while (!q.empty()){
        int u = q.front();
        q.pop();
        for (int v = 0; v < V; v++){
            if (visited[v] == false && graph[u][v].residual > 0){
                q.push(v);
                parent[v] = u;
                visited[v] = true;
            }
                
        }
    }
    return (visited[t] == true);
}

void printSolution(vector<int>& dist)
{
   printf("Vertex   Distance from Source\n");
   for (int i = 0; i < dist.size(); i++)
      printf("%d \t\t %d\n", i, dist[i]);
}

typedef  pair<int, int> ii;
bool findAugmentedPath_djkstra(vector<vector<GraphNode> >& graph, int s, int t, int parent[]){

    int V = graph.size();
    vector<int> cost(V, INF); 
    cost[s] = 0; //
    priority_queue<ii, vector<ii>, greater<ii> > pq;
    pq.push(ii(0, s));
    bool visited[V];
    memset(visited, 0, sizeof(visited));
    visited[s] = true;

    while (!pq.empty()){
        ii front = pq.top(); 
        pq.pop();
        int d = front.first;
        int u = front.second;
        if ( d == cost[u] ) {
            for (int j = 0; j < V; j++) {
                GraphNode v = graph[u][j];
                if (graph[u][j].residual > 0 && cost[u] + v.cost < cost[j]) {
                    cost[j] = cost[u] + v.cost;
                    pq.push(ii(cost[j], j));
                    parent[j] = u;
                    visited[j] = true;
                }
            }
        }
    }
    //printSolution (cost);    
    return (visited[t] == true);
}

bool findPath(vector< vector<GraphNode> >& graph, int s, int t, int parent[]){
   //return findAugmentedPath_bfs(graph, s, t, parent);
   return findAugmentedPath_djkstra(graph, s, t, parent);
}

int fordFulkerson(vector< vector<GraphNode> >& graph, int s, int t)
{

    int u, v;
    int V = graph.size();
    for (u = 0; u < V; u++) {
        for (v =0; v < V; v++) {
            graph[u][v].residual = graph[u][v].capacity;
        }
    }

    int parent[V]; // This array stores path found by BFS/DFS/Djkstra
    
    int max_flow = 0;

    while (findPath(graph, s, t, parent)) {
        int path_flow = INT_MAX;
        cout << t << "<-";
        for (v = t; v != s; v=parent[v]){
            u = parent[v];
            cout << u << "<-" ;
            path_flow = min(path_flow, graph[u][v].residual);
        }
        cout << endl;

        for (v = t; v != s; v=parent[v]) {
            u = parent[v];
            graph[u][v].residual -= path_flow;
            graph[v][u].residual += path_flow;

            graph[u][v].flow += path_flow;
            graph[v][u].flow -= path_flow;
        }

        max_flow += path_flow;
    }

    return max_flow;

}

void printFlowGraph(vector< vector<GraphNode> >& graph) {

    int V = graph.size();
    for (int i = 0; i < V; i++) {
        for (int j = 0; j < V; j++) {
            cout << graph[i][j].flow << " ";
        }
        cout << endl;
    }
}
int main() {

    vector< vector<GraphNode> > graph;

    for (int i = 0; i < 6; i++) {
        vector<GraphNode> vg;
        for (int j = 0; j < 6; j++) {
            GraphNode g = GraphNode();
            if (i == 0) {
                if (j == 1) { g.capacity = 16; g.cost = 100;}
                if (j == 2) { g.capacity = 13; g.cost = 2;}
            }
            if (i == 1) {
                if (j == 2) { g.capacity = 10; g.cost = 3;}
                if (j == 3) { g.capacity = 12; g.cost = 100;}
            }
            if (i == 2) {
                if (j == 1) { g.capacity = 4; g.cost = 5;}
                if (j == 4) { g.capacity = 14; g.cost = 1;}
            }
            if (i == 3) {
                if (j == 2) { g.capacity = 9; g.cost = 7;}
                if (j == 5) { g.capacity = 20; g.cost = 100;}
            }
            if (i == 4) {
                if (j == 3) { g.capacity = 7; g.cost = 9;}
                if (j == 5) { g.capacity = 4; g.cost = 1;}
            }
            vg.push_back(g);
        }
        graph.push_back(vg);
    }

    int maxFlow = fordFulkerson(graph, 0, 5); 
    cout << "The maximum possible flow is " << maxFlow << "\n";
    cout << "Flow Graph is: " << endl;
    printFlowGraph(graph);
    cout << "Done!" << endl;
    return 0;
}
