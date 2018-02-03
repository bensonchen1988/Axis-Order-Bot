import peewee
import configAxisDB
import configAxis
from peewee import *
import logging
from urllib import parse
import os
import axisUtility
import datetime
import axisRank as ranker

logger = logging.getLogger('axis_order_db')
hdlr = logging.FileHandler('axis_order_db.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

if os.environ.get('DATABASE_URL'):
	db_url = os.environ.get('DATABASE_URL')
	creds = parse.urlparse(db_url)
	db = PostgresqlDatabase(creds.path[1:], user = creds.username, password = creds.password, host = creds.hostname, port = creds.port)
else:
	db = PostgresqlDatabase(configAxisDB.schema, 
		user=configAxisDB.username, 
		password=configAxisDB.password, 
		host=configAxisDB.host)


class Members(Model):
	class Meta:
		database = db
		db_table = "members"
		primary_key = CompositeKey('username', 'member_number')

	username = CharField()
	member_number = IntegerField()
	referrals = IntegerField()
	time_last_prayed = DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))

class Replied_Comments(Model):
	class Meta:
		database = db
		db_table = "replied_comments"
	comment_id = CharField(primary_key=True)
	time_entered = DateTimeField(default=datetime.datetime.now)

def get_replied_comments_model(subreddit_name):
	setattr(Replied_Comments._meta, "db_table", "replied_comments_"+subreddit_name)
	return Replied_Comments

#Returns the join order of this member.
#assumes user exists
def get_member_number(username):
	db.connect()
	logger.info("connected - member number for "+username)
	result = Members.select(Members.member_number).where(Members.username == username).execute()
	answer = str(result.next().member_number)
	db.close()
	logger.info("disconnected - member number for "+username+", result: "+answer)
	return answer

def get_member_number_for_signup():
	if not Members.select().exists():
		return 1;

	result = Members.select(fn.max(Members.member_number)).execute()
	return result.next().member_number+1

def has_faith(username):
	db.connect()
	#logger.info("connected - faith check for "+username)
	result = Members.select().where(Members.username == username).exists()
	db.close()
	#logger.info("disconnected - faith check for "+username+", result: "+str(result))
	return result

def has_comment(comment_id, subreddit):
	db.connect()
	#logger.info("connected - comment dupe check for "+comment_id)
	result = get_replied_comments_model(subreddit).select().where(Replied_Comments.comment_id == comment_id).exists()
	db.close()
	#logger.info("disconnected - comment dupe check for "+comment_id+", result: "+str(result))
	return result


#assumes user doesn't exist
def member_signup(user_name):
	db.connect()
	member_number_result = get_member_number_for_signup()
	Members.create(username = user_name, member_number = member_number_result, referrals = 0)
	db.close()
	logger.info("member signed up: "+user_name)

def record_comment(target_id, subreddit_name):
	db.connect()
	get_replied_comments_model(subreddit_name).create(comment_id = target_id)
	db.close()
	logger.info("comment id recorded: "+target_id)

def get_number_of_members():
	db.connect()
	result = str(Members.select().count())
	db.close()
	return result

#assumes user exists
def get_referrals(user_name):
	db.connect()
	result = Members.select(Members.referrals).where(Members.username == user_name).execute()
	answer = str(result.next().referrals)
	db.close()
	return answer

#assumes user exists
def add_points(user_name, points):
	db.connect()
	logger.info(user_name +" gained "+str(points)+" "+axisUtility.add_s(points, "point"))
	update_target = Members.select().where(Members.username == user_name).get()
	update_target.referrals += points
	update_target.save()
	db.close()

def close_connection():
	db.close()


def safe_create_tables():
	db.connect()
	tablelist = [Members]
	for subreddit_name in configAxis.subreddits:
		tablelist.append(get_replied_comments_model(subreddit_name))
	db.create_tables(tablelist, safe=True)
	db.close()

#trims the replied_comments table down to the %threshold% newest comments
def trim_replied_comments(threshold):
	db.connect()
	for subreddit_name in configAxis.subreddits:
		n = 0
		for comment in get_replied_comments_model(subreddit_name).select().order_by(Replied_Comments.time_entered.desc()):
			n += 1
			if n > threshold:
				print("deleting comment "+comment.comment_id+" from "+getattr(get_replied_comments_model(subreddit_name)._meta, "db_table"))
				logger.info("deleting comment "+comment.comment_id+" from "+subreddit_name)
				comment.delete_instance()
	db.close()

#checks if 22 hours has passed since last prayer
#assumes user exists
def can_receive_points_from_prayer(user_name):
	db.connect()
	result = Members.select().where(Members.username == user_name).execute()
	member = result.next()
	db.close()
	return member.time_last_prayed <= datetime.datetime.now() - datetime.timedelta(hours = 22)


def update_pray_time(user_name):
	db.connect()
	update_target = Members.select().where(Members.username == user_name).get()
	update_target.time_last_prayed = datetime.datetime.now()
	update_target.save()
	db.close()

def get_ranking_string():
	db.connect()

	if not Members.select().exists():
		db.close()
		return "We have no members..... Aqua-sama? AQUA-SAMA!?!?!? AQUA-SAMAAAAAAAAAAAAAAAAAAA!!!!"

	result_string = "Rank| Member | Axis Points | Rank Title\n"
	result_string += "---|---|---|----\n"
	rank = 1
	current_points = _get_max_points()
	members_string = ""
	for member in Members.select().order_by(Members.referrals.desc(), Members.username.asc()):
		if member.referrals < current_points:
			result_string += str(rank)+"| "+members_string[:-2]+" | "+str(current_points)+" | "+ranker.get_rank(current_points)+"\n"
			members_string = member.username+", "
			current_points = member.referrals
			rank += 1
		else:
			members_string += member.username+", "

	result_string += str(rank)+"| "+members_string[:-2]+" | "+str(current_points)+" | "+ranker.get_rank(current_points)+"\n"
	
	db.close()
	return result_string

def _get_max_points():
	result = Members.select(fn.max(Members.referrals)).execute()
	return result.next().referrals

def get_all_member_usernames():
	db.connect()
	result_list = []
	for member in Members.select(Members.username):
		result_list.append(member.username)
	db.close()
	return result_list
