def id_to_ordinal(id):
	"""Converts an id to an ordinal, e.g. 0 -> 1st, 1 -> 2nd, etc."""
	if id == 0:
		return "1st"
	elif id == 1:
		return "2nd"
	elif id == 2:
		return "3rd"
	elif id == 3:
		return "final"
	else:
		raise ValueError(f"Invalid id: {id}")

