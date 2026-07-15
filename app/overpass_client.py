import urllib.request
import urllib.parse
import json
import math

class OverpassClient:
    def __init__(self):
        self.endpoint = "https://overpass-api.de/api/interpreter"
        self.elevation_endpoint = "https://api.opentopodata.org/v1/srtm30m"

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000 # meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_pedestrian_infrastructure(self, lat, lon, radius=200):
        """
        Fetches pedestrian paths, steps, elevators, and platforms within a radius.
        """
        bbox = f"{lat - radius/111000},{lon - radius/(111000*math.cos(math.radians(lat)))},{lat + radius/111000},{lon + radius/(111000*math.cos(math.radians(lat)))}"
        query = f"""
        [out:json];
        (
          way["highway"~"footway|steps|pedestrian"]({bbox});
          node["highway"~"elevator"]({bbox});
          way["public_transport"="platform"]({bbox});
        );
        out body;
        >;
        out skel qt;
        """
        data = urllib.parse.urlencode({'data': query})
        url = f"{self.endpoint}?{data}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'EuskalTransit/1.0'})
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching Overpass data: {e}")
            return None

    def get_elevation(self, lat, lon):
        """
        Fetches elevation in meters from Open Topo Data.
        """
        url = f"{self.elevation_endpoint}?locations={lat},{lon}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and "results" in data and data["results"]:
                    return data["results"][0]["elevation"]
        except Exception as e:
            print(f"Error fetching Elevation data: {e}")
        return 0.0

    def parse_graph(self, overpass_json):
        """
        Parses overpass json into a local graph of nodes and edges.
        Returns nodes dict and edges list.
        """
        nodes = {}
        for element in overpass_json.get('elements', []):
            if element['type'] == 'node':
                nodes[element['id']] = {
                    'lat': element['lat'],
                    'lon': element['lon'],
                    'tags': element.get('tags', {})
                }
        
        edges = []
        for element in overpass_json.get('elements', []):
            if element['type'] == 'way':
                node_refs = element.get('nodes', [])
                tags = element.get('tags', {})
                is_steps = tags.get('highway') == 'steps'
                for i in range(len(node_refs) - 1):
                    u = node_refs[i]
                    v = node_refs[i+1]
                    if u in nodes and v in nodes:
                        dist = self.haversine(nodes[u]['lat'], nodes[u]['lon'], nodes[v]['lat'], nodes[v]['lon'])
                        # Base walking speed ~ 1.4 m/s. Steps are slower.
                        time_seconds = dist / 1.4
                        if is_steps:
                            time_seconds *= 2.0 # Penalize steps
                        
                        edges.append({
                            'u': u, 'v': v, 
                            'distance': dist, 
                            'time_s': time_seconds,
                            'is_steps': is_steps
                        })
        return nodes, edges

if __name__ == "__main__":
    client = OverpassClient()
    # Test with Abando station coordinates
    lat, lon = 43.2608, -2.9275
    print("Fetching Abando infrastructure...")
    data = client.get_pedestrian_infrastructure(lat, lon, 100)
    if data:
        nodes, edges = client.parse_graph(data)
        print(f"Found {len(nodes)} nodes and {len(edges)} pedestrian edges.")
        print(f"Elevation at Abando: {client.get_elevation(lat, lon)} meters")
