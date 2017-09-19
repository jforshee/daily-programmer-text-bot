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

# Process the /r/dailyprogrammer submission.
def process_submission(submission):
    title = submission.title
    match = daily_component_pattern.match(title)
    if match is not None:
        title_components = parse_daily_components(match)
        shortlink = submission.shortlink
        print('Building message for {0} - {1}'.format(title_components[2], shortlink))

        message = build_message(title_components, shortlink)
        send_message(message)

# Parses a matched submission into its components.
# See: daily_component_pattern
def parse_daily_components(match):
    return (match.group('date'),
            match.group('difficulty')[0],
            match.group('title'))

# Builds a message body from submission title components
# and a shortlink to the submission.
def build_message(title_components, shortlink):
    difficulty = title_components[1]
    title = title_components[2]
    trunc_title = (title[:72] + '...') if len(title) > 75 else title

    return '[{difficulty}] {trunc_title} - {link}'.format(difficulty=difficulty,
                                                          trunc_title=trunc_title,
                                                          link=shortlink)

# Sends a message body to a specified Twilio recipient.
def send_message(message):
    TWILIO.messages.create(to=TWILIO_TO,
                           from_=TWILIO_FROM,
                           body=message)

subreddit = REDDIT.subreddit('dailyprogrammer')
ignore = True
for submission in subreddit.stream.submissions(pause_after=0):
    if submission is None:
        ignore = False
        continue
    
    # Subreddit.stream does this dumb thing where it spits out a huge list of
    # historical submissions that we want to ignore on first run.
    print('Found submission {0}'.format(submission.title))
    if ignore:
        continue

    process_submission(submission)

