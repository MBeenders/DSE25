from pyvis.network import Network
reqs = {}

with open("reqs.csv", "r") as f:
	for line in f.readlines():
		split_line = [field.strip().replace("\xc2\xa0", " ") for field in line.strip().split("\t")]
		if len(split_line) >= 2:
			reqs[split_line[0]] = split_line[:]
			print(split_line[0])

net = Network(height='95vh', width='100%', bgcolor='#223', font_color='#222', directed=True)

for key in reqs:
	shape = "circle" if key.startswith("STK") else "box"
	color = "#ffffff" if key.startswith("STK") else "#add8e6"
	net.add_node(key, label=key, shape = shape, title=reqs[key][1],
				 color = color, mass = 1)
print(len(reqs))

for key in reqs:
	if len(reqs[key]) == 5:
		parent = reqs[key][4]
		if parent not in reqs:

			net.add_node(parent, label=parent, shape = "circle", 
				 color = "#FF0000", mass = 1)


		net.add_edge(parent, key, color="#90ee90")


net.show("viz.html", notebook=False)