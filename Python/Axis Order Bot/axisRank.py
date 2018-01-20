#Giant Toad; 0~4
#SS: 5~9
#SM/M: 10~14
#DF: 15~19
#Pr: 20~24
#Hpr: 25~29
#MM: 30~34
#AP: 35~49
#KW: 50~999999999
def get_rank(points):
	if points < 5:
		return "Giant Toad"
	if points < 10:
		return "Street Solicitor"
	if points < 15:
		return "Soap Masseur/Masseuse"
	if points < 20:
		return "Devout Follower"
	if points < 25:
		return "Priest"
	if points < 30:
		return "High Priest"
	if points < 35:
		return "Megumin's Manatite"
	if points < 50:
		return "Cecily's Panties"
	return "Kazuma's Wallet"


def next_threshold(current_rank):
	if current_rank == "Giant Toad":
		return 5
	if current_rank == "Street Solicitor":
		return 10
	if current_rank == "Soap Masseur/Masseuse":
		return 15
	if current_rank == "Devout Follower":
		return 20
	if current_rank == "Priest":
		return 25
	if current_rank == "High Priest":
		return 30
	if current_rank == "Megumin's Manatite":
		return 35
	if current_rank == "Cecily's Panties":
		return 50
	if current_rank == "Kazuma's Wallet":
		return 100000000