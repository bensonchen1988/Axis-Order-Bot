import praw
import configAxis
import configAxisFlags
import axisRank as ranker
import axisUtility as util
import time
import os
import random
import datetime
import logging
import axis_database as db
import threading
from threading import Thread
from praw.models import Comment
from praw.models import Submission

logger = logging.getLogger('axis_order')
hdlr = logging.FileHandler('axis_order.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def bot_login():
	login= praw.Reddit(username = os.environ['REDDIT_USERNAME'], 
			password = os.environ['REDDIT_PASSWORD'], 
			client_id = os.environ['REDDIT_CLIENT_ID'], 
			client_secret = os.environ['REDDIT_CLIENT_SECRET'], 
			user_agent = "AxisCultCultivator")
	return login

def check_word(body):
	if any(x in body for x in configAxis.bot_call_words):
		return False

	for word in configAxis.hit_words:
		if(word in body):
			return True

	return False		

def run_bot(r):
	thread1 = Thread(target = check_inbox, args = ())
	thread2 = Thread(target = spread_the_word, args = ())
	thread1.start()
	print("t1 started")
	thread2.start()
	print("t2 started")
	thread1.join()
	thread2.join()
	print("sleeping for 10s")	
	time.sleep(10)

#Checks newest comments
def spread_the_word():
	try:
		for subreddit in configAxis.subreddits:
			for comment in r.subreddit(subreddit).comments(limit = 50):
				has_comment = db.has_comment(comment.id)
				if not has_comment:
					db.record_comment(comment.id)

				if check_word(comment.body.lower()) and not has_comment and comment.author != r.user.me() and not db.has_faith(comment.author.name):
					logger.info("Comment found: "+comment.id)
					invite(comment, None)

				if any(x in comment.body.lower() for x in configAxis.bot_call_words) and not has_comment and comment.author != r.user.me():
					member_functions(comment)

	except praw.exceptions.APIException as ex:
		print("praw.exceptions.APIException, sleeping for 60s") 
		print(str(ex))
		logger.error(str(ex))
		time.sleep(60)
		pass

#Checks inbox for comment applications or bot username-mention calls
#If configAxisFlags.inbox_forwading is True, forwards all unread messages to the username specified at configAxis.forward_username
def check_inbox():
	for message in r.inbox.unread():
		message.mark_read()
		if configAxisFlags.inbox_forwarding:
			forward_inbox(message)

		if "!join" in message.body.lower() and not db.has_comment(message.id):
			db.record_comment(message.id)
			sign_them_up(message)
			continue
		if "!stats" in message.body.lower() and not db.has_comment(message.id):
			#members only function
			if not db.has_faith(comment.author.name):
				message.reply(configAxis.not_a_member)
				return
			db.record_comment(message.id)
			reply_stats(message)
			continue
		if "!help" in message.body.lower() and not db.has_comment(message.id):
			db.record_comment(message.id)
			message.reply(get_help())
			continue
		if "/u/axis_order" in message.body.lower() and not db.has_comment(message.id):
			db.record_comment(message.id)
			if not db.has_faith(message.author.name):
				message.reply(configAxis.not_a_member)
			else:
				member_functions(message)
			continue

#Bot call parameter handling
def member_functions(comment):
	target_comment = comment.parent()
	#invites the author of the parent comment to this current comment if that person has not yet joined the order
	if "invite" in comment.body.lower():
		#members only function
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return
		logger.info(comment.author.name + " initiated an invite on "+target_comment.author.name)
		print(comment.author.name + " initiated an invite on "+target_comment.author.name)
		if db.has_faith(target_comment.author.name):
			comment.reply("Great news! "+target_comment.author.name+" is already a member of the holy Axis Order!" +get_footer())
		else:
			if type(target_comment) is praw.models.Submission:
				print("Submission invite")
				invite_submission(target_comment, comment)
			else:
				print("Comment invite")
				invite(target_comment, comment.author.name)
		return
	#replies stats of author of comment
	if "stats" in comment.body.lower():
		#members only function
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return
		reply_stats(comment)
		return

	#アクシズ教、教義！
	if any(x in comment.body.lower() for x in configAxis.teaching_hit_words):
		#members only function
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return

		if "all" in comment.body.lower() or "-a" in comment.body.lower():
			db.add_referral(comment.author.name, 2)
			comment.reply("You'ved gained 2 points for reciting all the teachings maniacally in one breath!: \n\n"+get_all_teachings()+get_footer())
		else:
			db.add_referral(comment.author.name, 1)
			comment.reply("You'ved gained 1 point for reciting the following teachings!: \n\n"+get_random_teaching()+get_footer())
		return

	#助けてよ~！！
	if "help" in comment.body.lower():
		comment.reply(get_help())

	#Someone wants to join via botcall LOL! GET SCAMMED BRUH
	if "join" in comment.body.lower():
		sign_them_up(comment)

def forward_inbox(message):
	r.redditor(configAxis.forward_username).message("Inbox forward from "+configAxis.username+", from "+message.author.name, message.body)

#Sends spam to target comment
def invite(comment, referralname):

	if comment.author == r.user.me():
		return

	print("Inviting comment")
	if referralname is None:
		comment.reply(get_invite_image()+get_footer())
	else:
		comment.reply(get_invite_image()+get_footer()+" ^("+configAxis.invitation+referralname+")")


	log_body = "Replied to user "+comment.author.name
	logger.info(log_body)

#Sends spam to target submission
def invite_submission(submission, inviting_comment):
	print("Inviting submission")
	submission.reply(get_invite_image()+get_footer()+" ^("+configAxis.invitation+inviting_comment.author.name+" )")
	logger.info("Replied to submission at "+submission.shortlink)
	print("Replied to submission at "+submission.shortlink)
	db.record_comment(submission.id)


def reply_stats(comment):
	points = int(db.get_referrals(comment.author.name))
	rank = ranker.get_rank(points)
	point_until_rank_up = ranker.next_threshold(rank) - points
	comment.reply("You are member #"+db.get_member_number(comment.author.name)+" of "+db.get_number_of_members()+", and you hold the rank of "+rank+", with "+str(points)+" "+util.add_s(points, "point")+"! Your next rank up is "+str(point_until_rank_up)+" "+util.add_s(point_until_rank_up, "point")+" away!!!")
		
def sign_them_up(message):
	if not db.has_faith(message.author.name):
		print("Found a sucker!: "+message.author.name+" "+message.id)
		db.member_signup(message.author.name)
		message.reply("WELCOME TO THE BLESSED AXIS ORDER! You are member #"+db.get_member_number(message.author.name)+"! May you receive the blessings of the Holy Water Goddess Aqua!")
		logger.info(message.author.name +" has joined Axis Order!")
		print(message.author.name +" has joined Axis Order!")
		if isinstance(message, Comment) and not isinstance(message.parent(), Submission):
				comment = r.comment(message.id)
				if configAxis.invitation in comment.parent().body:
					wordlist = comment.parent().body.split()
					db.add_referral(wordlist[-1][:-1], 5)
					logger.info(wordlist[-1][:-1]+" has been credited +5 points for the referral")
					print(wordlist[-1][:-1]+" has been credited +5 points for the referral")
	else:
		num_members_string = db.get_number_of_members()
		message.reply("Hello fellow faithful, it seems like you already belong to the wonderful Axis Order! You are member #"+db.get_member_number(message.author.name)+" of "+db.get_number_of_members()+" "+util.add_s(int(num_members_string), "member")+"!")
		

def get_footer():
	return "\n\n ***** \n\n ^(I am a bot created to spread faith for the wonderful and divine Water Goddess Aqua! Reply \"!join\" to this bot to join the blessed Axis Order today! We currently have "+db.get_number_of_members()+" followers! Reply !help for instructions, or message feedbacks to /u/"+configAxis.forward_username+"!)"

def get_invite_image():
	return "["+random.choice(configAxis.phrases)+"](https://imgur.com/a/ArJlZ) \n\n"

def get_random_teaching():
	return random.choice(configAxis.teachings)

def get_all_teachings():
	result = ""
	for teaching in configAxis.teachings:
		result += teaching+" \n\n"
	return result	

def get_help():
	result = ""
	result += "This bot can be called by username mention in any subreddit, or by the following keywords in "+get_subreddits()+": \n\n"
	for bot_call_word in configAxis.bot_call_words:
		result += bot_call_word+" "
	result += "\n\n"
	result += configAxis.help_two
	result += configAxis.help_table1
	result += configAxis.help_table2
	result += configAxis.help_table3
	result += configAxis.help_table4
	result += configAxis.help_table5
	result += configAxis.help_table6
	return result

def get_subreddits():
	result = ""
	for sub in configAxis.subreddits:
		result += "/r/"+sub+" "
	return result

r = bot_login()
db.safe_create_tables()

while True:
	try:
		run_bot(r)
	except (KeyboardInterrupt) as e:
		print("Manual quit")
		quit(0)
	except Exception as e:
		print("Megumin's Explosion created an exception; see log")
		try:
			db.close_connection()
		except:
			pass
		logger.exception(str(e))
		pass