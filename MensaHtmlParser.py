from html.parser import HTMLParser
import os.path
import MensaMealIngredient

class Parser(HTMLParser):
	tags = 0
	context = {}
	
	def getData(self):
		return self.data
		
	def handle_starttag(self, tag, attrs):
		# 
		# Tag-Zähler inkrementieren:
		# 
		self.tags += 1
		
	def handle_endtag(self, tag):
		# 
		# Prüfen, ob das Ende eines Kontexts erreicht ist:
		#  
		for ctx in self.context.items():
			if self.tags == ctx[1][1]:
				self.context[(ctx[0])] = (False, -1)
		# 
		# Tag-Zähler dekrementieren:
		# 
		self.tags -= 1
		
	def get_attr(self, attrs, name):
		for attr in attrs:
			if attr[0] == name:
				return attr[1]
		return None
		
	def enter_context(self, name):
		self.context[name] = (True, self.tags)
		
	def check_context(self, name):
		return self.context[name][0]

class OverviewParser(Parser, HTMLParser):
	context = {
		"spalterechts": (False, -1),
		"h1": (False, -1),
		"thead": (False, -1),
		"tbody": (False, -1),
		"text": (False, -1),
		"stoffe": (False, -1),
		"preise": (False, -1)
	}
	thead_num = 0
	data = {
		"date": None,
		"cafeterias": [ ]
	}
	ingredientsImgs = {
		"schweinefleisch.png": MensaMealIngredient.General.Pork,
		"rindfleisch.png": MensaMealIngredient.General.Beef,
		"fleischlos.png": MensaMealIngredient.General.NoMeat,
		"alkohol.png": MensaMealIngredient.General.Alcohol,
		"knoblauch.png": MensaMealIngredient.General.Garlic,
		"vegan.png": MensaMealIngredient.General.Vegan
	}
	
	def reinit(self):
		data = {
			"date": None,
			"cafeterias": [ ]
		}
	
	def handle_starttag(self, tag, attrs):
		super().handle_starttag(tag, attrs)
		# 
		# Prüfen, ob rechte Spalte erreicht ist:
		# 
		if tag == "div" and self.get_attr(attrs, "id") == "spalterechtsnebenmenue":
			self.enter_context("spalterechts")
		# 
		# Prüfen, ob wir uns in rechter Spalte befinden:
		# 
		if self.check_context("spalterechts"):
			# 
			# Prüfen, ob Überschrift erreicht ist:
			# 
			if tag == "h1":
				self.enter_context("h1")
			#
			# Prüfen, ob Tabellenkopf erreicht ist:
			# 
			if tag == "thead":
				self.enter_context("thead")
				self.thead_num = 0
			# 
			# Prüfen, ob Tabellenkörper erreicht ist:
			# 
			if tag == "tbody":
				self.enter_context("tbody")
			# 
			# Prüfen, ob wir uns im Tabellenkopf befinden:
			# 
			if self.check_context("thead"):
				self.thead_num += 1
			# 
			# Prüfen, ob wir uns im Tabellenkörper befinden:
			# 
			if self.check_context("tbody"):
				# 
				# Prüfen, ob Spalte mit Text / Inhaltsstoffen / Preisen erreicht ist:
				# 
				if tag == "td" and self.get_attr(attrs, "class") == "text":
					self.enter_context("text")
				if tag == "td" and self.get_attr(attrs, "class") == "stoffe":
					self.enter_context("stoffe")
				if tag == "td" and self.get_attr(attrs, "class") == "preise":
					self.enter_context("preise")
				# 
				# Prüfen, ob wir uns in Spalte mit Text befinden:
				# 
				if self.check_context("text"):
					if tag == "a":
						self.data["cafeterias"][-1]["meals"].append({
							"name": None,
							"url": self.get_attr(attrs, "href"),
							"ingredients": [],
							"prices": (None, None)
						})
				# 
				# Prüfen, ob wir uns in Spalte mit Inhaltsstoffen befinden:
				# 
				if self.check_context("stoffe"):
					if tag == "img":
						i = os.path.basename(self.get_attr(attrs, "src"))
						for img in self.ingredientsImgs.items():
							if img[0] == i:
								self.data["cafeterias"][-1]["meals"][-1]["ingredients"].append(img[1])
		
	def handle_data(self, data):
		# 
		# Prüfen, ob wir uns in der Überschrift befinden:
		# 
		if self.check_context("h1"):
			self.data["date"] = data.split(", den ", 2)[1] # FIXME
		# 
		# Prüfen, ob wir uns im Tabellenkopf befinden:
		# 
		if self.check_context("thead"):
			if self.thead_num == 3:
				self.data["cafeterias"].append({
					"name": data,
					"meals": []
				})
		# 
		# Prüfen, ob wir uns in Spalte mit Text befinden:
		# 
		if self.check_context("text"):
			self.data["cafeterias"][-1]["meals"][-1]["name"] = data
		# 
		# Prüfen, ob wir uns in Spalte mit Preisen befinden:
		# 
		if self.check_context("preise"):
			try:
				p = float(data.replace("/", "").replace(" ", "").replace(",", "."))
				t = self.data["cafeterias"][-1]["meals"][-1]["prices"]
				if t[0] != None:
					self.data["cafeterias"][-1]["meals"][-1]["prices"] = (t[0], p)
				else:
					self.data["cafeterias"][-1]["meals"][-1]["prices"] = (p, None)
			except ValueError:
				print("Error parsing price:", data) # FIXME

class DetailParser(Parser, HTMLParser):
	context = {
		"detailsrechts": (False, -1),
		"li": (False, -1)
	}
	data = []
	ingredientsPatterns = {
		"(1)":  MensaMealIngredient.Additives.Colorant,
		"(2)":  MensaMealIngredient.Additives.Preservative,
		"(3)":  MensaMealIngredient.Additives.Antioxidant,
		"(4)":  MensaMealIngredient.Additives.FlavorEnhancer,
		"(5)":  MensaMealIngredient.Additives.Sulfur,
		"(6)":  MensaMealIngredient.Additives.Blackened,
		"(7)":  MensaMealIngredient.Additives.Waxed,
		"(8)":  MensaMealIngredient.Additives.Phosphate,
		"(9)":  MensaMealIngredient.Additives.Sweetener,
		"(10)": MensaMealIngredient.Additives.Phenylalanine,
		"(A)":  MensaMealIngredient.Allergens.Gluten,
		"(B)":  MensaMealIngredient.Allergens.Shellfish,
		"(C)":  MensaMealIngredient.Allergens.Eggs,
		"(D)":  MensaMealIngredient.Allergens.Fish,
		"(E)":  MensaMealIngredient.Allergens.Peanuts,
		"(F)":  MensaMealIngredient.Allergens.Soy,
		"(G)":  MensaMealIngredient.Allergens.Milk,
		"(H)":  MensaMealIngredient.Allergens.Nuts,
		"(I)":  MensaMealIngredient.Allergens.Celery,
		"(J)":  MensaMealIngredient.Allergens.Mustard,
		"(K)":  MensaMealIngredient.Allergens.Sesame,
		"(L)":  MensaMealIngredient.Allergens.Sulphite,
		"(M)":  MensaMealIngredient.Allergens.Lupine,
		"(N)":  MensaMealIngredient.Allergens.Molluscs
	}
	
	def reinit(self):
		self.data = []
		
	def handle_starttag(self, tag, attrs):
		super().handle_starttag(tag, attrs)
		# 
		# Prüfen, ob rechte Spalte erreicht ist:
		# 
		if tag == "div" and self.get_attr(attrs, "id") == "speiseplandetailsrechts":
			self.enter_context("detailsrechts")
		# 
		# Prüfen, ob wir uns in rechter Spalte befinden:
		if self.check_context("detailsrechts"):
			# 
			# Prüfen, ob Listenelement erreicht ist:
			# 
			if tag == "li":
				self.enter_context("li")
		
	def handle_data(self, data):
		#
		# Prüfen, ob wir uns in Listenelement befinden:
		# 
		if self.check_context("li"):
			for i in self.ingredientsPatterns.items():
				if data.find(i[0]) > -1:
					self.data.append(i[1])
