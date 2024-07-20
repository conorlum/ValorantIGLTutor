economies = {}






def recording(total_economy):
	if total_economy in economies:
		economies[total_economy] += 1
	else:
		economies[total_economy] = 1

def buy_from_economy(economy, enemy_economy):
	if 