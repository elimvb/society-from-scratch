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
	

def convert_rankings_to_preferences(liking_score_dict): 
	"""Converts the rankings outputted from simulation into proper preferences format for stable matching algorithm."""
	men_pref = {'Carson Crimson': None, 'Ashley Amber': None, 'Goldie Goldenrod': None, 'Sam Slate': None}
	women_pref = {'Cora Coral': None, 'Azealia Azure': None, 'Emma Emerald': None, 'Indie Indigo': None}
	for person in liking_score_dict:
		if person in men_pref:
			cora = (person['Cora Coral'], 'Cora Coral')
			azealia = (person['Azealia Azure'], 'Azealia Azure')
			emma = (person['Emma Emerald'], 'Emma Emerald')
			indie = (person['Indie Indigo'], 'Indie Indigo')
			preference = sorted([cora, azealia, emma, indie], reverse=True)
			men_pref[person] = [preference[0][1], preference[1][1], preference[2][1], preference[3][1]]
		elif person in women_pref:
			carson = (person['Carson Crimson'], 'Carson Crimson')
			sam = (person['Sam Slate'], 'Sam Slate')
			goldie = (person['Goldie Goldenrod'], 'Goldie Goldenrod')
			ashley = (person['Ashley Amber'], 'Ashley Amber')
			preference = sorted([carson, sam, goldie, ashley], reverse=True)
			men_pref[person] = [preference[0][1], preference[1][1], preference[2][1], preference[3][1]]
	return men_pref, women_pref

def matches(list_1):
    matches = {}
    for i in list_1:
        matches[i] = ''
    return matches

def start_match():
    while len(Men_Free) > 0:
        for i in key_list:
            match_algo(i)
	    
def match_algo(man):
    for woman in Men_Pref[man]:
        if woman not in list(Matches.values()):
            Matches[man] = woman
            Men_Free.remove(man)
            print('{} is no longer a free man and is tentatively engaged to {} !'.format(man, woman))
            break
        elif woman in list(Matches.values()):
            current_suitor = list(Matches.keys())[list(Matches.values()).index(woman)]
            w_list = Women_Pref.get(woman)
            if w_list.index(man) < w_list.index(current_suitor):
                Matches[man] = woman
                Men_Free.remove(man)
                Matches[current_suitor] = ''
                Men_Free.append(current_suitor)
                print('{} was earlier engaged to {} but now is engaged to {}! '.format(woman, current_suitor, man))
                return

def stable_matching_algorithm(Men_Pref, Women_Pref):
	Men = list(Men_Pref.keys())
	Women = list(Women_Pref.keys())

	Men_Free = list(Men)
	Women_Free = list(Women)

	Matches = matches(l1)
	key_list = list(Matches.keys())

	while len(Men_Free) > 0:
		for man in key_list:
			for woman in Men_Pref[man]:
				if woman not in list(Matches.values()):
					Matches[man] = woman
					Men_Free.remove(man)
					print('{} is no longer a free man and is tentatively engaged to {} !'.format(man, woman))
					break
				elif woman in list(Matches.values()):
					current_suitor = list(Matches.keys())[list(Matches.values()).index(woman)]
					w_list = Women_Pref.get(woman)
					if w_list.index(man) < w_list.index(current_suitor):
						Matches[man] = woman
						Men_Free.remove(man)
						Matches[current_suitor] = ''
						Men_Free.append(current_suitor)
						print('{} was earlier engaged to {} but now is engaged to {}! '.format(woman, current_suitor, man))



	print('\n ')
    print('Stable Matching Finished ! Happy engagement !')
    for man in Matches.keys():
        print('{} is engaged to {} !'.format(man, Matches[man]))


def log_and_print(log_fw, message):
	"""Prints a message and also writes it to a log file."""
	print(message)
	log_fw.write(message + "\n")
	log_fw.flush()
