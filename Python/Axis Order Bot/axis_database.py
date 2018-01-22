import peewee
import configAxisDB
from peewee import *
import logging
from urllib import parse
import os
import axisUtility
import datetime

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

class Replied_Comments(Model):
	class Meta:
		database = db
		db_table = "replied_comments"
	comment_id = CharField(primary_key=True)
	time_entered = DateTimeField(default=datetime.datetime.now)

#Returns the join order of this member.
#ASSUMES MEMBER DOES EXIST ALREADY
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

	result = Members.select(fn.max(Members.member_number))
	return result.next()+1

def has_faith(username):
	db.connect()
	#logger.info("connected - faith check for "+username)
	result = Members.select().where(Members.username == username).exists()
	db.close()
	#logger.info("disconnected - faith check for "+username+", result: "+str(result))
	return result

def has_comment(comment_id):
	db.connect()
	#logger.info("connected - comment dupe check for "+comment_id)
	result = Replied_Comments.select().where(Replied_Comments.comment_id == comment_id).exists()
	db.close()
	#logger.info("disconnected - comment dupe check for "+comment_id+", result: "+str(result))
	return result


def member_signup(user_name):
	db.connect()
	id = get_member_number_for_signup()
	Members.create(username = user_name, member_number = id, referrals = 0)
	db.close()
	logger.info("member signed up: "+user_name)

def record_comment(id):
	db.connect()
	Replied_Comments.create(comment_id = id)
	db.close()
	logger.info("comment id recorded: "+id)

def get_number_of_members():
	db.connect()
	result = str(Members.select().count())
	db.close()
	return result

def get_referrals(user_name):
	db.connect()
	result = Members.select(Members.referrals).where(Members.username == user_name).execute()
	answer = str(result.next().referrals)
	db.close()
	return answer

def add_referral(user_name, points):
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
	db.create_tables([Members, Replied_Comments], safe=True)
	db.close()

#trims the replied_comments table down to the %threshold% newest comments
def trim_replied_comments(threshold):
	db.connect()
	n = 0
	for comment in Replied_Comments.select().order_by(Replied_Comments.time_entered.desc()):
		n += 1
		if n > threshold:
			print("deleting comment "+comment.comment_id)
			logger.info("deleting comment "+comment.comment_id)
			comment.delete_instance()
	db.close()

