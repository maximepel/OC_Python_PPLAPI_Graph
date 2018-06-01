import json
import math
import matplotlib.pyplot as plt

## Classe qui va charger 100.000 agents obtenus dans un JSON depuis le site PPLAPI qui est un faux réseau social
class Agent:
	
	## Constructeur
	def __init__(self, position, **attributes):
		self.position = position
		# Pour chaque attribut parsé du JSON : attribuer à l'instance de classe sa valeur (et son nom d'attribut)
		for attr_name, attr_value in attributes.items():
			setattr(self, attr_name, attr_value)



## Classe qui va situer les positions des Agents
class Position:

	def __init__(self, longitude_degres, latitude_degres):
		self.longitude_degres = longitude_degres
		self.latitude_degres = latitude_degres


	@property
	def longitude(self):
		return self.longitude_degres * math.pi / 180


	@property
	def latitude(self):
		return self.longitude_degres * math.pi / 180



## Classe qui va symboliser des zones et associer les gens en fonction de leur position
class Zone:

	ZONES = []
	MIN_LONGITUDE_DEGREES = -180 ## -180 à 180° pour faire le tour de la Terre
	MAX_LONGITUDE_DEGREES = 180
	MIN_LATITUDE_DEGREES = -90 ## -90 à 90° pour faire l'aller du pole Nord au pole Sud (demi tour Terre)
	MAX_LATITUDE_DEGREES = 90
	WIDTH_DEGREES = 1 # graduation longitudinale
	HEIGHT_DEGREES = 1 # graduation latitudinale
	EARTH_RADIUS_KILOMETERS = 6371

	def __init__(self, corner1, corner2):
		self.corner1 = corner1
		self.corner2 = corner2
		self.inhabitants = [] # zone inhabitée par défaut


	def add_inhabitant(self, inhabitant):
		self.inhabitants.append(inhabitant)


	@property
	def population(self):
		return len(self.inhabitants)

	@property
	def width(self):
		return abs(self.corner1.longitude - self.corner2.longitude) * self.EARTH_RADIUS_KILOMETERS

	@property
	def height(self):
		return abs(self.corner1.latitude - self.corner2.latitude) * self.EARTH_RADIUS_KILOMETERS

	@property
	def area(self):
		return self.width * self.height

	def population_density(self):
		return self.population / self.area

	# _ signifie méthode protected ( __ signifie private)
	@classmethod #static => self devient "cls"
	def _initialize_zones(cls):
		for latitude in range(cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.HEIGHT_DEGREES):
			## Pour chaque longitude comprise entre -180 et 180 (de 1 en 1)
			for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.WIDTH_DEGREES):
				bottom_left_corner = Position(longitude, latitude)
				top_right_corner = Position(longitude + cls.WIDTH_DEGREES, latitude + cls.HEIGHT_DEGREES)
				zone = Zone(bottom_left_corner, top_right_corner)
				cls.ZONES.append(zone)


	def contains(self, position):
		return position.longitude >= min(self.corner1.longitude, self.corner2.longitude) and position.longitude < max(self.corner1.longitude, self.corner2.longitude) and \
			position.latitude >= min(self.corner1.latitude, self.corner2.latitude) and position.latitude < max(self.corner1.latitude, self.corner2.latitude)


	@classmethod #static 
	def find_zone_that_contains(cls, position):
		
		if not cls.ZONES:
			Zone._initialize_zones() # 64800 zones (360*180)

		longitude_index = int((position.longitude_degres - cls.MIN_LONGITUDE_DEGREES)/ cls.WIDTH_DEGREES) # x-(-180)/1
		latitude_index = int((position.latitude_degres - cls.MIN_LATITUDE_DEGREES)/ cls.HEIGHT_DEGREES)
		longitude_bins = int((cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES) # 180-(-180) / 1
		zone_index = latitude_index * longitude_bins + longitude_index

		# Vérification
		zone = cls.ZONES[zone_index]
		assert zone.contains(position)

		return zone

	def average_agreeableness(self): # Retourne la somme des agreabilités divisé par le nombre d'habitants
		if not self.inhabitants: 
			return 0 # évite division par 0 : c'est pêché
		"""
		## Ceci est un "List Comprehension" : [inhabitant.agreeableness for inhabitant in self.inhabitants]
		## Equivalent de (creer liste vide) + (for sur self.inhabitants) + (liste.append(inhabitant.agreeableness))
		"""
		return sum([inhabitant.agreeableness for inhabitant in self.inhabitants]) / self.population

## CLASSE PARENT pour l'affichage d'un graph
class BaseGraph:

	def __init__(self):
		self.title = "Représentation de l'agréabilité en fonction des zones terrestres"
		self.x_label = "X-axis label"
		self.y_label = "Y-ordonnate label"
		self.show_grid = True

	def show(self, zones):
		x_values, y_values = self.xy_values(zones)
		plt.plot(x_values, y_values, ".") ## "." donne un graph de points [void documentation]
		plt.xlabel(self.x_label)
		plt.ylabel(self.y_label)
		plt.title(self.title)
		plt.grid(self.show_grid)
		plt.show()

	def xy_values(self, zones):
		raise NotImplementedError



## CLASSE ENFANT (Heritage) entre parenthèses
class AgreeablenessGraph(BaseGraph):
	def __init__(self): # C'est une redéfinition du constructeur suite à l'héritage de BaseGraph
		super().__init__() # On appelle le constructeur parent pour show_grid essentiellement
		self.title = "Répartition"
		self.x_label = "Densité de population"
		self.y_label = "Agréabilité"

	def xy_values(self, zones):
		x_values = [zone.population_density() for zone in zones]
		y_values = [zone.average_agreeableness() for zone in zones]
		return x_values, y_values





def main():
	
	## Pour chaque { attr_individu }, { attr_individu } JSON
	# On charge le fichier JSON "agents-100k.json" grâce au module json (import)
	for agent_attributes in json.load(open("agents-100k.json")):
		## On récupère d'abord longitude et latitude (on les retire du dictionnary) et on en fait une instance de position
		longitude = agent_attributes.pop("longitude")
		latitude = agent_attributes.pop("latitude")
		position = Position(longitude, latitude)

		## ** pour un dictionnaire
		agent = Agent(position, **agent_attributes)

		zone = Zone.find_zone_that_contains(position)
		zone.add_inhabitant(agent)

	agreeableness_graph = AgreeablenessGraph()
	agreeableness_graph.show(Zone.ZONES)

## Appel du programme
main()