# Axis-Order-Bot
この素晴らしい世界にアクシズ教信を！

This bot is now running on Heroku! 

Uses Peewee as ORM, with PostgreSQL as the DB.

This is still a work in progress.

TODO: 
- Rank-based permission to various functions. Function idea: generate image macro
- Ways to spend points (Buy skills/functions?)
- ~Think of a way to get around Heroku's 10000 row limit in DB without paying. ~ DONE...?*

*fix for replied_comments table has been implemented (limited at configAxis.comment_limit = 100 newest comments). 
Probably no practical way to get around the limit without paying for the members table
