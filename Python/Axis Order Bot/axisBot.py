import praw
import configAxis
import configAxisFlags
import axisRank as ranker
import axisUtility as util
import time
import os
import datetime
import logging
import axis_database as db
from praw.models import Comment
from praw.models import Submission
import axisMembers as members
import traceback

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
	check_inbox()
	print("checked inbox")
	spread_the_word()
	print("checked newest "+str(configAxis.comment_limit)+" comments")
	db.trim_replied_comments(configAxis.comment_limit)
	print("finished trimming replied comments")
	update_rankings()
	print("updated rankings wiki at "+configAxis.wiki_subreddit)
	print("sleeping for 10s")	
	time.sleep(10)

#Checks newest comments
def spread_the_word():
	try:
		for subreddit in configAxis.subreddits:
			for comment in r.subreddit(subreddit).comments(limit = configAxis.comment_limit):
				has_comment = db.has_comment(comment.id)

				if check_word(comment.body.lower()) and not has_comment and comment.author != r.user.me() and not db.has_faith(comment.author.name):
					db.record_comment(comment.id)
					logger.info("Comment found: "+comment.id)
					#bot default invite
					bot_invite(comment, None)

				if any(x in comment.body.lower() for x in configAxis.bot_call_words) and not has_comment and comment.author != r.user.me():
					db.record_comment(comment.id)
					parse_parameters(comment)

	except praw.exceptions.APIException as ex:
		print("praw.exceptions.APIException, sleeping for 60s") 
		print(str(ex))
		logger.error(str(ex))
		time.sleep(60)
		pass

#Checks inbox for comment applications or bot username-mention calls
#If configAxisFlags.inbox_forwarding is True, forwards all unread messages to the username specified at configAxis.forward_username
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
			members.member_stats(message)
			db.record_comment(message.id)
			continue
		if "!help" in message.body.lower() and not db.has_comment(message.id):
			db.record_comment(message.id)
			message.reply(util.get_help())
			continue
		if "/u/axis_order" in message.body.lower() and not db.has_comment(message.id):
			db.record_comment(message.id)
			if not db.has_faith(message.author.name):
				message.reply(configAxis.not_a_member)
			else:
				parse_parameters(message)
			continue
		#admin only function (all-member broadcasting)
		if "!broadcast" in message.body.lower() and message.author.name == configAxis.forward_username:
			bot_broadcast(message)

#broadcasts message to all members
def bot_broadcast(message):
	message_body = message.body.replace("!broadcast ", "")
	member_count = 0;
	for username in db.get_all_member_usernames():
		r.redditor(username).message("Axis Order Broadcast Message", message_body)
		member_count += 1
	r.redditor(configAxis.forward_username).message("Broadcast result", "The following message has been broadcasted to "+str(member_count)+" members: \n\n"+message_body)

def bot_invite(comment):

	if comment.author == r.user.me():
		return

	print("Inviting comment")
	comment.reply(util.get_invite_image()+util.get_footer())
	log_body = "Replied to user "+comment.author.name
	logger.info(log_body)


#Bot call parameter handling
def parse_parameters(comment):
	#invites the author of the parent comment to this current comment if that person has not yet joined the order
	if "invite" in comment.body.lower():
		#members only function
		members.member_invite(comment)
		return
	#replies stats of author of comment
	if "stats" in comment.body.lower():
		#members only function
		members.member_stats(comment)
		return

	#アクシズ教、教義！
	if any(x in comment.body.lower() for x in configAxis.teaching_hit_words):
		#members only function
		members.member_pray(comment)
		return

	#助けてよ~！！
	if "help" in comment.body.lower():
		comment.reply(get_help())

	#Someone wants to join via botcall LOL! GET SCAMMED BRUH
	if "join" in comment.body.lower():
		sign_them_up(comment)


def forward_inbox(message):
	r.redditor(configAxis.forward_username).message("Inbox forward from "+configAxis.username+", from "+message.author.name, message.body)


		
def sign_them_up(message):
	if not db.has_faith(message.author.name):
		print("Found a sucker!: "+message.author.name+" "+message.id)
		db.member_signup(message.author.name)
		message.reply("WELCOME TO THE BLESSED AXIS ORDER! You are member #"+db.get_member_number(message.author.name)+"! May you receive the blessings of the Holy Water Goddess Aqua!")
		logger.info(message.author.name +" has joined Axis Order!")
		print(message.author.name +" has joined Axis Order!")
		if isinstance(message, Comment) and not isinstance(message.parent(), Submission):
				comment = r.comment(message.id)
				if configAxis.invitation in comment.parent().body and comment.parent().author is r.user.me():
					wordlist = comment.parent().body.split()
					db.add_points(wordlist[-1][:-1], 5)
					logger.info(wordlist[-1][:-1]+" has been credited +5 points for the referral")
					print(wordlist[-1][:-1]+" has been credited +5 points for the referral")
	else:
		num_members_string = db.get_number_of_members()
		message.reply("Hello fellow faithful, it seems like you already belong to the wonderful Axis Order! You are member #"+db.get_member_number(message.author.name)+" of "+db.get_number_of_members()+" "+util.add_s(int(num_members_string), "member")+"!")
		



def update_rankings():
	wiki = r.subreddit(configAxis.wiki_subreddit).wiki[configAxis.wiki_name]
	wiki.edit(db.get_ranking_string())

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
		traceback.print_exc()
		pass