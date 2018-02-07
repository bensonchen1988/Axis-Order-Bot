import configAxis
import random
import axis_database as db
import string

def add_s(points, word):
	if points > 1:
		return word+"s"
	return word


def get_footer():
	return "\n\n ***** \n\n ^(I am a bot created to spread faith for the wonderful and divine Water Goddess Aqua! Reply \"!join\" to this bot to join the blessed Axis Order today! We currently have "+str(1000000+int(db.get_number_of_members()))+" followers! Reply !help for instructions, or message feedbacks to /u/"+configAxis.forward_username+"!) ^| [^Help ^Wiki](https://www.reddit.com/r/"+configAxis.wiki_subreddit+"/wiki/index) ^| [^Point ^Rankings](https://www.reddit.com/r/"+configAxis.wiki_subreddit+"/wiki/"+configAxis.wiki_name+") ^| [^Official ^Pray ^Thread]("+configAxis.pray_thread_url+")"

def get_invite_image():
	return "["+random.choice(configAxis.phrases)+"]("+configAxis.invite_image+") \n\n"

def get_single_teaching(comment):
	text = comment.body.lower()
	if "fault" in text:
		return configAxis.teachings[0]
	if "run" in text:
		return configAxis.teachings[1]
	if "regret" in text:
		return configAxis.teachings[2]
	if "neet" in text:
		return configAxis.teachings[3]
	if "glut" in text:
		return configAxis.teachings[4]
	if "happy" in text:
		return configAxis.teachings[5]
	if "slay" in text:
		return configAxis.teachings[6]
	if "pad" in text:
		return configAxis.teachings[7]
	if "loli" in text:
		return configAxis.teachings[8]

	return random.choice(configAxis.teachings)

def get_all_teachings():
	result = ""
	for teaching in configAxis.teachings:
		result += teaching+" \n\n"
	return result	


def get_help():
	result = ""
	result += "This bot can be called by username mention in any subreddit, or by the following keywords in /r/konosuba: \n\n"
	for bot_call_word in configAxis.bot_call_words:
		result += "**"+bot_call_word+"** "
	result += "\n\n"
	result += configAxis.help_two
	result += configAxis.help_table1
	result += configAxis.help_table2
	result += configAxis.help_table3
	result += configAxis.help_table4
	result += configAxis.help_table5
	result += configAxis.help_table6
	result += configAxis.help_table7
	result += get_footer()
	return result

def get_subreddits():
	result = ""
	for sub in configAxis.subreddits:
		result += "/r/"+sub+" "
	return result

def escape_reddit_chars(target_string):
	result = target_string.replace("_", "\_")

	return result

def unescape_reddit_chars(target_string):
	return target_string.replace("\\", "")