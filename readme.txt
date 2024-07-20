Givens:
No game will progress to OT as this is not in scope.  all games will end with at most a score of 11-13.  meaning there will be a max of 24 rounds played before a winner is decided.  

simulation will progress with stages:
record economy: at a minimun will be a 10 length array with each of the agents economies.  I don't want more info as I want to simplify this into a few number of states
buy stage: what is bought will be based on team economy and personal economy with laid out simple rules
	rules of engagement:
		simplification is util is 600 for all agents (or at least 600 credits will be used on average)
		pistol: buy based on most picked loadout from VCT rejakvik (simplification is 750 credits used)
		pistol loss: full save only util
		pistol win: 50 + 3000 + kills = (3050 - 4050) 1600 + gun (1600, 2050, 2900) 0-2 kills = money - 3050 (util + half + bulldog), 3-5 kills is 0 remaining (full buy in)
		full buy: personal econs must be able to buy 3900 + util for full team or if enough money to buy for someone
		buy for next: if any personal econs are below the 3900 + util threshold and above 3900 + util - round bonus (1900, 2400, 2900) as this is already calculated for us in client
		full save: buy util 
		if any scenarios get through error out.

	



simulation of round:
	does the game need to end?
	variables that affect economy:
		death
		kills
		util usage
		spike planted
		shield broken
		round outcome + loss streak bonus



