from praw import Reddit

import os
import re
import twilio.rest

# Reddit constants
REDDIT_ID = os.environ['REDDIT_ID']
REDDIT_AUTH = os.environ['REDDIT_AUTH']
REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_PASS = os.environ['REDDIT_PASS']
REDDIT = Reddit(client_id=REDDIT_ID,
                client_secret=REDDIT_AUTH,
                username=REDDIT_USER,
                password=REDDIT_PASS,
                user_agent='testscript')

# Twilio constants
# Client construction assumes that TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are both set
TWILIO_TO = os.environ['TWILIO_TO']
TWILIO_FROM = os.environ['TWILIO_FROM']
TWILIO = twilio.rest.Client()

# Typical format for daily submission titles is akin to:
#     [2017-09-04] Challenge #330 [Easy] Surround the circles
# Components:
#     [{date}] Challenge #{num} [{difficulty}] {title}
daily_component_pattern = re.compile(r"""\s*\[(?P<date>.*)\] 
                                         .*                         # challenge number (don't care)
                                         \[(?P<difficulty>.*)\]
                                         \s*(?P<title>.*)""", re.VERBOSE)

def process_submission(submission):
    if 'Monthly' not in submission.title:
        title_components = parse_daily_components(submission.title)
        message = build_message(title_components, submission.shortlink)

        send_message(message)
    else:
        print('Skipping Monthly challenge...')

def parse_daily_components(title):
    match = daily_component_pattern.match(title)
    return (match.group('date'),
            match.group('difficulty')[0],
            match.group('title'))

def build_message(title_components, shortlink):
    difficulty = title_components[1]
    title = title_components[2]
    trunc_title = (title[:72] + '...') if len(title) > 75 else title

    return '[{difficulty}] {trunc_title} - {link}'.format(difficulty=difficulty,
                                                          trunc_title=trunc_title,
                                                          link=shortlink)

def send_message(message):
    TWILIO.messages.create(to=TWILIO_TO,
                           from_=TWILIO_FROM,
                           body=message)

subreddit = REDDIT.subreddit('dailyprogrammer')
for submission in subreddit.stream.submissions():
    process_submission(submission)

