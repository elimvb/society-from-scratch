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
	

# def convert_rankings_to_preferences(liking_score_dict): 
# 	""""""


def log_and_print(log_fw, message):
	"""Prints a message and also writes it to a log file."""
	print(message)
	log_fw.write(message + "\n")
	log_fw.flush()
