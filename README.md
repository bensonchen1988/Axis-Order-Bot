# Axis-Order-Bot
この素晴らしい世界にアクシズ教信を！

This bot is now running on Heroku! 

Uses Peewee as ORM, with PostgreSQL as the DB.

This is still a work in progress.

TODO: 
- ~Implement "dailies" using timestamped fields. ~ DONE
- Rank-based permission to various functions
- Ways to spend points
- Output and update rankings to its own subreddit's wiki
- ~Think of a way to get around Heroku's 10000 row limit in DB without paying. ~ DONE...?*

*fix for replied_comments table has been implemented (limited at configAxis.comment_limit = 100 newest comments), probably no way to get around the limit without paying for the members table
