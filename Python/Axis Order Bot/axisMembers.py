import axisUtility as util
import axisRank as ranker
import axis_database as db
import configAxis
import praw
from praw.models import Comment
from praw.models import Submission
import logging

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
	if "all" in comment.body.lower() or "-a" in comment.body.lower():
		all_message = ""
		if db.can_receive_points_from_prayer(comment.author.name):
			points = 2
			if comment.submission.fullname == configAxis.pray_submission_id:
				points = 3
			db.add_points(comment.author.name, points)
			all_message += "You've gained "+str(points)+" Axis Points for reciting all the teachings maniacally in one breath!: \n\n"
			db.update_pray_time(comment.author.name)
		comment.reply(all_message+util.get_all_teachings()+util.get_footer())
	else:
		single_message = ""
		if db.can_receive_points_from_prayer(comment.author.name):
			points = 1
			if comment.submission.fullname == configAxis.pray_submission_id:
				points = 2
			db.add_points(comment.author.name, points)
			single_message += "You've gained "+str(points)+" Axis "+util.add_s(points, "Point")+" for reciting the following teachings!: \n\n"
			db.update_pray_time(comment.author.name)
		comment.reply(single_message+util.get_random_teaching()+util.get_footer())

#Sends spam to target comment
def _invite_comment(comment, referralname):

	if comment.author.name == configAxis.username:
		return

	print("Inviting comment")
	if referralname is None:
		comment.reply(util.get_invite_image()+util.get_footer())
	else:
		comment.reply(util.get_invite_image()+util.get_footer()+" ^("+configAxis.invitation+referralname+")")


	log_body = "Replied to user "+comment.author.name
	logger.info(log_body)

#Sends spam to target submission
def _invite_submission(submission, inviting_comment):
	print("Inviting submission")
	submission.reply(util.get_invite_image()+util.get_footer()+" ^("+configAxis.invitation+inviting_comment.author.name+")")
	logger.info("Replied to submission at "+submission.shortlink)
	print("Replied to submission at "+submission.shortlink)


def _reply_stats(comment):
	points = int(db.get_referrals(comment.author.name))
	rank = ranker.get_rank(points)
	point_until_rank_up = ranker.next_threshold(rank) - points
	comment.reply("You are member #"+db.get_member_number(comment.author.name)+" of "+db.get_number_of_members()+", and you hold the rank of "+rank+", with Axis "+str(points)+" "+util.add_s(points, "Point")+"! Your next rank up is "+str(point_until_rank_up)+" Axis "+util.add_s(point_until_rank_up, "Point")+" away!!!")
