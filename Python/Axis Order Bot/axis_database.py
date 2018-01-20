import peewee
import configAxisDB
from peewee import *
import logging

logger = logging.getLogger('axis_order_db')
hdlr = logging.FileHandler('axis_order_db.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

db = PostgresqlDatabase(configAxisDB.schema, user=configAxisDB.username, password=configAxisDB.password, host=configAxisDB.host)


class Members(Model):
	class Meta:
		database = db
		db_table = "members_postgres"
		primary_key = CompositeKey('username', 'member_number')

	username = CharField()
	member_number = IntegerField()
	referrals = IntegerField()

class Replied_Comments(Model):
	class Meta:
		database = db
		db_table = "replied_comments_postgres"
	comment_id = CharField()

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
	Members.create(username = user_name, referrals = 0)
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

def add_referral(user_name):
	db.connect()
	update_target = Members.select().where(Members.username == user_name).get()
	update_target.referrals += 1
	update_target.save()
	db.close()

def close_connection():
	db.close()


def safe_create_tables():
	db.create_tables([Members, Replied_Comments], safe=True)