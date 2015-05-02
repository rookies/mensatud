#!/usr/bin/python3
import urllib.request, json
import MensaHtmlParser
import MensaMealIngredient

def send_request(url):
	req = urllib.request.Request(
		url,
		headers={
			"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
	})
	sock = urllib.request.urlopen(req)
	return sock

if __name__ == "__main__":
	baseurl = "http://www.studentenwerk-dresden.de/mensen/speiseplan/"
	parser1 = MensaHtmlParser.OverviewParser()
	parser2 = MensaHtmlParser.DetailParser()
	parser1.feed(send_request(baseurl + "w1-d1.html").read().decode("utf-8"))
	data = parser1.getData()
	# Vorsortierung:
	i = 0
	for caf in data["cafeterias"]:
		tmp = []
		for m in caf["meals"]:
			if (m["ingredients"].count(MensaMealIngredient.General.Vegan) != 0 or m["ingredients"].count(MensaMealIngredient.General.NoMeat) != 0):
				tmp.append(m)
		data["cafeterias"][i]["meals"] = tmp
		i += 1
	# Nähere Informationen holen:
	i = 0
	for caf in data["cafeterias"]:
		j = 0
		for m in caf["meals"]:
			if m["url"] != None:
				parser2.reinit()
				parser2.feed(send_request(baseurl + m["url"]).read().decode("utf-8"))
				data["cafeterias"][i]["meals"][j]["ingredients"].extend(parser2.getData())
			j += 1
		i += 1
	# Endgültige Sortierung:
	i = 0
	for caf in data["cafeterias"]:
		tmp = []
		for m in caf["meals"]:
			if (m["ingredients"].count(MensaMealIngredient.Allergens.Eggs) == 0 and m["ingredients"].count(MensaMealIngredient.Allergens.Milk) == 0):
				tmp.append(m)
		data["cafeterias"][i]["meals"] = tmp
		i += 1
	#print(json.dumps(data, indent=2))
	print("Vegan am %s:" % data["date"])
	for caf in data["cafeterias"]:
		if len(caf["meals"]) != 0:
			print("%s:\n\t%s" % (caf["name"], "\n\t".join(map(lambda m: "%s (%.2f €)" % (m["name"], m["prices"][0]), caf["meals"]))))
