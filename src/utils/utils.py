def generate_unique_id():
	with open(".jobcount", "r") as f:
		idx = int(f.read())
	with open(".jobcount", "w") as f:
		f.write(str(idx + 1))
	return idx
