import axisUtility as util
import axisRank as ranker
import axis_database as db
import configAxis
import praw
from praw.models import Comment
from praw.models import Submission
import logging
import axisMeme

logger = logging.getLogger('axis_order')
hdlr = logging.FileHandler('axis_order.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)


def member_invite(comment):
	target_comment = comment.parent()
	logger.info(comment.author.name + " initiated an invite on "+target_comment.author.name)
	print(comment.author.name + " initiated an invite on "+target_comment.author.name)
	if db.has_faith(target_comment.author.name):
		comment.reply("Great news! "+target_comment.author.name+" is already a member of the holy Axis Order!" +util.get_footer())
	else:
		if type(target_comment) is praw.models.Submission:
			print("Submission invite")
			_invite_submission(target_comment, comment)
		else:
			print("Comment invite")
			_invite_comment(target_comment, comment.author.name)

def member_stats(comment):
	_reply_stats(comment)

def member_pray(comment):
	print("submission id: "+comment.submission.fullname)

	points = 0
	if comment.submission.fullname == configAxis.pray_submission_id:
		points += 1

	if "all" in comment.body.lower() or "-a" in comment.body.lower():
		all_message = ""
		if db.can_receive_points_from_prayer(comment.author.name):
			points += 2
			db.add_points(comment.author.name, points)
			all_message += "You've gained "+str(points)+" Axis Points for reciting all the teachings maniacally in one breath!: \n\n"
			db.update_pray_time(comment.author.name)
		comment.reply(all_message+util.get_all_teachings()+util.get_footer())
	else:
		single_message = ""
		if db.can_receive_points_from_prayer(comment.author.name):
			points += 1
			db.add_points(comment.author.name, points)
			single_message += "You've gained "+str(points)+" Axis "+util.add_s(points, "Point")+" for reciting the following teachings!: \n\n"
			db.update_pray_time(comment.author.name)
		comment.reply(single_message+util.get_single_teaching(comment)+util.get_footer())

def member_meme(comment, r):
	current_points = int(db.get_referrals(comment.author.name))
	if current_points < configAxis.points_to_meme:
		comment.reply("Sorry, but you must be of rank \""+ranker.get_rank(configAxis.points_to_meme)+"\" ("+str(configAxis.points_to_meme)+" Axis Points) or higher to request a Meme Strike!"+util.get_footer())
		return

	text = comment.body.lower()

	if "!memestrike " in comment.body.lower():
		#targetted memestriking on a specific post at the url the user provides
		if current_points < configAxis.points_to_memestrike:
			comment.reply("Sorry, but you must be of rank \""+ranker.get_rank(configAxis.points_to_memestrke)+"\" ("+str(configAxis.points_to_memestrike)+" Axis Points) or higher to request a Meme Strike!"+util.get_footer())
			return
		#assumed parameter format: !axisbot !memestrike URL memetext
		#split with space, get index = 2 as url, process 
		space_split_text = text.split()
		split_index = 1
		min_arg_count = 2
		if "!axis" in text:
			split_index += 1
			min_arg_count = 3
		if len(space_split_text) < min_arg_count:
			comment.reply("It seems that something went wrong! Please make sure you supply a proper full reddit URL when meme striking!"+util.get_footer())
			return
		url = space_split_text[split_index]
		if "www.reddit" not in url:
			comment.reply("It seems that something went wrong! Please make sure you supply a proper full reddit URL when meme striking!"+util.get_footer())
			return
		#hacky id extraction.
		comment_id = url[len(url)-8:len(url)-1]
		target_post = None


		try:
			target_post = r.comment(comment_id)
			target_post.parent()
		except:
			try:
				target_post = r.submission(url = url)
			except:
				comment.reply("It seems that something went wrong! Please make sure you supply a proper full reddit URL when meme striking!"+util.get_footer())
				return

		index = text.find(url+" ")
		#blacklist check
		if any(x == target_post.subreddit.display_name for x in configAxis.blacklisted_subreddits):
			comment.reply("Sorry, you can not order a meme strike into a proactively blacklisted subreddit!")
			return

		try:
			if index == -1 or text[index+len(url+" "):] == "":
				target_post.reply(axisMeme.get_meme_hyperlink(" ")+util.get_footer_meme()+" ^(This is a Meme Strike ordered by member /u/"+comment.author.name+")")
				return
			target_post.reply(axisMeme.get_meme_hyperlink(text[index+len(url+" "):])+util.get_footer_meme()) #+" ^(This is a Meme Strike ordered by member /u/"+comment.author.name+")"
		except:
			comment.reply("It seems that something went wrong! This bot may have been banned from the subreddit you're trying to meme strike!"+util.get_footer())
	else:
		#normal memeing that replies to user via botcalls or username mention
		index = text.find("!meme ")
		if index == -1 or text[index+6:] == "":
			comment.reply(axisMeme.get_meme_hyperlink(" ")+util.get_footer())
			return
		comment.reply(axisMeme.get_meme_hyperlink(text[index+6:])+util.get_footer())

#Sends spam to target comment
def _invite_comment(comment, referralname):

	if comment.author.name == configAxis.username:
		return

	print("Inviting comment")
	if referralname is None:
		comment.reply(util.get_invite_image()+util.get_footer())
	else:
		comment.reply(util.get_invite_image()+util.get_footer()+" ^("+configAxis.invitation+util.escape_reddit_chars(referralname)+")")


	log_body = "Replied to user "+comment.author.name
	logger.info(log_body)

#Sends spam to target submission
def _invite_submission(submission, inviting_comment):
	print("Inviting submission")
	submission.reply(util.get_invite_image()+util.get_footer()+" ^("+configAxis.invitation+util.escape_reddit_chars(inviting_comment.author.name)+")")
	logger.info("Replied to submission at "+submission.shortlink)
	print("Replied to submission at "+submission.shortlink)


def _reply_stats(comment):
	points = int(db.get_referrals(comment.author.name))
	rank = ranker.get_rank(points)
	point_until_rank_up = ranker.next_threshold(rank) - points
	comment.reply("You are member #"+db.get_member_number(comment.author.name)+" of "+db.get_number_of_members()+", and you hold the rank of "+rank+", with "+str(points)+" Axis "+util.add_s(points, "Point")+"! Your next rank up is "+str(point_until_rank_up)+" Axis "+util.add_s(point_until_rank_up, "Point")+" away!!!")
