import math
import heapq
from collections import defaultdict

class EnrutamientoHibrido:
    def __init__(self, gestor):
        self.gestor = gestor
        self.grafo = defaultdict(list)
        self.nodos = {}
        # Cost weights
        self.PESO_ESCALERAS = 2.5
        self.VELOCIDAD_PEATON_MS = 1.4
        self.VELOCIDAD_TREN_MS = 15.0 # Approx 54 km/h

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def construir_grafo_gtfs(self):
        """
        Builds the basic routing graph from GTFS data in gestor.
        """
        print("Construyendo grafo base GTFS...")
        
        todas_las_estaciones = {**self.gestor.estaciones_globales, **self.gestor.estaciones_metro, **self.gestor.estaciones_bus}
        for stop_id, parada in todas_las_estaciones.items():
            self.nodos[stop_id] = {
                'lat': parada.latitud,
                'lon': parada.longitud,
                'tipo': 'parada',
                'nombre': parada.nombre
            }
            
        # Metro L1
        for i in range(len(self.gestor.l1_stops_ordered) - 1):
            origen = self.gestor.l1_stops_ordered[i]
            destino = self.gestor.l1_stops_ordered[i+1]
            if origen in self.nodos and destino in self.nodos:
                dist = self._haversine(
                    self.nodos[origen]['lat'], self.nodos[origen]['lon'],
                    self.nodos[destino]['lat'], self.nodos[destino]['lon']
                )
                tiempo = dist / self.VELOCIDAD_TREN_MS
                self.grafo[origen].append({'destino': destino, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tren', 'linea': 'L1'})
                self.grafo[destino].append({'destino': origen, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tren', 'linea': 'L1'})
                
        # Metro L2
        for i in range(len(self.gestor.l2_stops_ordered) - 1):
            origen = self.gestor.l2_stops_ordered[i]
            destino = self.gestor.l2_stops_ordered[i+1]
            if origen in self.nodos and destino in self.nodos:
                dist = self._haversine(
                    self.nodos[origen]['lat'], self.nodos[origen]['lon'],
                    self.nodos[destino]['lat'], self.nodos[destino]['lon']
                )
                tiempo = dist / self.VELOCIDAD_TREN_MS
                self.grafo[origen].append({'destino': destino, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tren', 'linea': 'L2'})
                self.grafo[destino].append({'destino': origen, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tren', 'linea': 'L2'})
                
        # Tranvía
        for i in range(len(self.gestor.tranvia_stops_ordered) - 1):
            origen = self.gestor.tranvia_stops_ordered[i]
            destino = self.gestor.tranvia_stops_ordered[i+1]
            if origen in self.nodos and destino in self.nodos:
                dist = self._haversine(
                    self.nodos[origen]['lat'], self.nodos[origen]['lon'],
                    self.nodos[destino]['lat'], self.nodos[destino]['lon']
                )
                tiempo = dist / (15 / 3.6) # Velocidad aprox tranvía 15km/h
                self.grafo[origen].append({'destino': destino, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tranvia', 'linea': 'TR'})
                self.grafo[destino].append({'destino': origen, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'tranvia', 'linea': 'TR'})

        # Bilbobus
        for origen, destino, linea in self.gestor.bus_edges:
            if origen in self.nodos and destino in self.nodos:
                dist = self._haversine(
                    self.nodos[origen]['lat'], self.nodos[origen]['lon'],
                    self.nodos[destino]['lat'], self.nodos[destino]['lon']
                )
                tiempo = dist / (15000 / 3600)  # 15 km/h urban bus speed estimate
                self.grafo[origen].append({'destino': destino, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'bus', 'linea': linea})

        # Enlaces Peatonales Intermodales (Transbordos)
        print("Calculando transbordos peatonales multimodales (< 400m)...")
        todas_las_paradas = list(self.nodos.keys())
        for i in range(len(todas_las_paradas)):
            for j in range(i + 1, len(todas_las_paradas)):
                n1 = todas_las_paradas[i]
                n2 = todas_las_paradas[j]
                
                dist = self._haversine(
                    self.nodos[n1]['lat'], self.nodos[n1]['lon'],
                    self.nodos[n2]['lat'], self.nodos[n2]['lon']
                )
                
                # Conectar estaciones si están a menos de 400 metros caminando
                if dist <= 400.0:
                    tiempo = dist / self.VELOCIDAD_PEATON_MS
                    self.grafo[n1].append({'destino': n2, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'peatonal'})
                    self.grafo[n2].append({'destino': n1, 'distancia': dist, 'tiempo': tiempo, 'tipo': 'peatonal'})


    def integrar_topologia_peatonal(self, overpass_client, lat, lon, radius=500):
        """
        Fetches and integrates pedestrian graph for a specific area (e.g. intermodal station).
        """
        data = overpass_client.get_pedestrian_infrastructure(lat, lon, radius)
        if not data: return
        
        osm_nodes, osm_edges = overpass_client.parse_graph(data)
        
        for n_id, n_data in osm_nodes.items():
            str_id = f"osm_{n_id}"
            self.nodos[str_id] = {
                'lat': n_data['lat'],
                'lon': n_data['lon'],
                'tipo': 'peatonal',
                'osm_id': n_id
            }
            
        for edge in osm_edges:
            u, v = f"osm_{edge['u']}", f"osm_{edge['v']}"
            coste = edge['time_s']
            
            # Simple elevation penalty approximation (could be improved with real elevation API per node)
            if edge['is_steps']:
                coste *= self.PESO_ESCALERAS
                
            self.grafo[u].append({'destino': v, 'distancia': edge['distance'], 'tiempo': coste, 'tipo': 'peatonal'})
            self.grafo[v].append({'destino': u, 'distancia': edge['distance'], 'tiempo': coste, 'tipo': 'peatonal'})

        # Connect GTFS stops to nearest pedestrian nodes
        for stop_id, stop_data in self.nodos.items():
            if stop_data['tipo'] == 'parada':
                closest_osm = None
                min_dist = float('inf')
                for osm_id, osm_data in osm_nodes.items():
                    dist = self._haversine(stop_data['lat'], stop_data['lon'], osm_data['lat'], osm_data['lon'])
                    if dist < min_dist:
                        min_dist = dist
                        closest_osm = f"osm_{osm_id}"
                
                if closest_osm and min_dist < 100: # Max 100m distance to snap
                    tiempo = min_dist / self.VELOCIDAD_PEATON_MS
                    self.grafo[stop_id].append({'destino': closest_osm, 'distancia': min_dist, 'tiempo': tiempo, 'tipo': 'enlace'})
                    self.grafo[closest_osm].append({'destino': stop_id, 'distancia': min_dist, 'tiempo': tiempo, 'tipo': 'enlace'})


    def calcular_ruta_a_estrella(self, id_origen, id_destino):
        """
        A* routing algorithm prioritizing time, with penalties for transfers.
        """
        if id_origen not in self.nodos or id_destino not in self.nodos:
            return None
            
        def heuristica(nodo_actual):
            return self._haversine(
                self.nodos[nodo_actual]['lat'], self.nodos[nodo_actual]['lon'],
                self.nodos[id_destino]['lat'], self.nodos[id_destino]['lon']
            ) / self.VELOCIDAD_TREN_MS # Optimistic time

        # cola de prioridad: (costo_f, costo_g, id_nodo, linea_previa)
        open_set = []
        heapq.heappush(open_set, (0, 0, id_origen, None))
        
        came_from = {}
        g_score = {node: float('inf') for node in self.nodos}
        g_score[id_origen] = 0

        while open_set:
            current_f, current_g, current, linea_previa = heapq.heappop(open_set)

            if current == id_destino:
                return self._reconstruir_ruta(came_from, current)

            for arista in self.grafo.get(current, []):
                vecino = arista['destino']
                peso = arista['tiempo']
                
                # Penalización por transbordo
                if arista['tipo'] == 'tren' and linea_previa and linea_previa != arista['linea']:
                    peso += 180 # 3 min transfer penalty
                elif arista['tipo'] == 'peatonal':
                    peso *= 1.2 # Peatonal preference penalty vs train if equal time

                tentative_g = current_g + peso

                if tentative_g < g_score[vecino]:
                    came_from[vecino] = (current, arista)
                    g_score[vecino] = tentative_g
                    f_score = tentative_g + heuristica(vecino)
                    heapq.heappush(open_set, (f_score, tentative_g, vecino, arista.get('linea')))

        return None

    def _reconstruir_ruta(self, came_from, current):
        ruta = []
        tiempo_total_peatonal = 0
        tiempo_total_tren = 0
        
        while current in came_from:
            prev_node, arista = came_from[current]
            ruta.insert(0, {
                'desde': prev_node,
                'hasta': current,
                'desde_nombre': self.nodos[prev_node].get('nombre', 'Punto Peatonal'),
                'hasta_nombre': self.nodos[current].get('nombre', 'Punto Peatonal'),
                'detalle': arista
            })
            if arista['tipo'] in ['peatonal', 'enlace']:
                tiempo_total_peatonal += arista['tiempo']
            else:
                tiempo_total_tren += arista['tiempo']
            current = prev_node
            
        return {
            'segmentos': ruta,
            'tiempo_peatonal_s': tiempo_total_peatonal,
            'tiempo_tren_s': tiempo_total_tren,
            'tiempo_total_s': tiempo_total_peatonal + tiempo_total_tren
        }
