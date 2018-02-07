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
	#TEMPORARY 200 limit
	db.trim_replied_comments(configAxis.comment_limit+100)
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
				has_comment = db.has_comment(comment.id, subreddit)

				if check_word(comment.body.lower()) and not has_comment and comment.author != r.user.me() and not db.has_faith(comment.author.name) and not any(x == subreddit for x in configAxis.manual_subreddits):
					db.record_comment(comment.id, subreddit)
					logger.info("Comment found: "+comment.id)
					#bot default invite
					bot_invite(comment)

				if any(x in comment.body.lower() for x in configAxis.bot_call_words) and not has_comment and comment.author != r.user.me():
					db.record_comment(comment.id, subreddit)
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

		if "!join" in message.body.lower():
			sign_them_up(message)
			continue
		if "!stats" in message.body.lower():
			#members only function
			members.member_stats(message)
			continue
		if "!help" in message.body.lower():
			message.reply(util.get_help())
			continue
		if "/u/axis_order" in message.body.lower():
			if any(x == message.subreddit.display_name for x in configAxis.blacklisted_subreddits):
				print("blacklisted subreddit: "+message.subreddit.display_name)
				r.redditor(message.author.name).message("Subreddit is blacklisted!", "Sorry, you've attempted to summon me into /r/"+message.subreddit.display_name+", which is blacklisted!")
				continue
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
#Allows multiple parameter call
def parse_parameters(comment):
	#助けてよ~！！
	if "!help" in comment.body.lower():
		comment.reply(util.get_help())

	#Someone wants to join via botcall LOL! GET SCAMMED BRUH
	if "!join" in comment.body.lower():
		sign_them_up(comment)

	#=========MEMBERS ONLY FUNCTION START============
	#invites the author of the parent comment to this current comment if that person has not yet joined the order
	if "!invite" in comment.body.lower():
		#Faith check
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return	
		#members only function
		members.member_invite(comment)

	#アクシズ教、教義！
	if any(x in comment.body.lower() for x in configAxis.teaching_hit_words):
		#Faith check
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return	
		#members only function
		members.member_pray(comment)

	#replies stats of author of comment
	if "!stats" in comment.body.lower():
		#Faith check
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return	
		#members only function
		members.member_stats(comment)

	if "!meme" in comment.body.lower():
		#Faith check
		if not db.has_faith(comment.author.name):
			comment.reply(configAxis.not_a_member)
			return	
		#members only function
		members.member_meme(comment)


	#=========MEMBERS ONLY FUNCTION END============



def forward_inbox(message):
	if isinstance(message, Comment):
		r.redditor(configAxis.forward_username).message("Inbox forward from "+configAxis.username+", from "+message.author.name, message.body+"\n\n  "+message.context)
	else:
		r.redditor(configAxis.forward_username).message("Inbox forward from "+configAxis.username+", from "+message.author.name, message.body)


def send_exception(body):
	r.redditor(configAxis.forward_username).message("Megumin's Explosion Created An Exception!", body)

		
def sign_them_up(message):
	if not db.has_faith(message.author.name):
		print("Found a sucker!: "+message.author.name+" "+message.id)
		db.member_signup(message.author.name)
		message.reply("WELCOME TO THE BLESSED AXIS ORDER! You are member #"+db.get_member_number(message.author.name)+"! Go forth and earn Axis Points by praying or inviting others to join (check the Help Wiki linked below)! May you receive the blessings of the Holy Water Goddess Aqua!" +util.get_footer())
		logger.info(message.author.name +" has joined Axis Order!")
		print(message.author.name +" has joined Axis Order!")
		if isinstance(message, Comment) and not isinstance(message.parent(), Submission):
			comment = r.comment(message.id)
			if configAxis.invitation in comment.parent().body and comment.parent().author.name == r.user.me().name:
				wordlist = comment.parent().body.split()
				username = util.unescape_reddit_chars(wordlist[-1][:-1])
				db.add_points(username, 5)
				logger.info(username+" has been credited +5 points for the referral")
				print(username+" has been credited +5 points for the referral")
	else:
		num_members_string = db.get_number_of_members()
		message.reply("Hello fellow faithful, it seems like you already belong to the wonderful Axis Order! You are member #"+db.get_member_number(message.author.name)+" of "+db.get_number_of_members()+" "+util.add_s(int(num_members_string), "member")+"!")
		



def update_rankings():
	wiki = r.subreddit(configAxis.wiki_subreddit).wiki[configAxis.wiki_name]
	number_of_members = "There are currently "+db.get_number_of_members()+" members in the Axis Order!\n\n"
	wiki.edit(number_of_members+db.get_ranking_string())

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
		send_exception(traceback.format_exc())
		pass