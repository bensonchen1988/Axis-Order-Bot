import configAxisRank

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

	index = 0;
	for i in range(0, len(configAxisRank.thresholds)):
		index = i
		if points >= configAxisRank.thresholds[i]:
			continue
		break
	return configAxisRank.thresholds_ranks[index]


def next_threshold(current_rank):
	return configAxisRank.thresholds[configAxisRank.thresholds_ranks.index(current_rank)]