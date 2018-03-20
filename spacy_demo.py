from flask import Flask
from flask_ask import Ask, statement, question

import numpy as np

app = Flask(__name__)
app.config['ASK_VERIFY_REQUESTS'] = False
ask = Ask(app, '/')

#app.config['ASK_VERIFY_REQUESTS'] = False

import logging

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

#  GETTING A TIME AT A CITY
from datetime import datetime
from geopy import geocoders
from tzwhere import tzwhere
from pytz import timezone


def hello():
#def hello(firstname):
    firstname = 'dave'
    speech_text = "Hello %s" % firstname
    return statement(speech_text).simple_card('Hello', speech_text)

def r_help():
    speech_text = "ask what time is it, in a city. or ask me how I am feeling."
    return question(speech_text).simple_card('Hello', speech_text)




# Spacy NLP voice routing
import en_core_web_sm
nlp = en_core_web_sm.load()

CLASSES={
    "help": [
        "help",
        "i am lost",
        "help me"
    ],
    "time": [
        "what time is it",
        "what time is it in london",
        "when is it now",
        "what is the time"
    ],
    "mood": [
        "how are you doing",
        "what mood are you in",
        "what do you think"
    ]
}


# If spacy is less confident then 75% then its an unknown utterance.
THRESHOLD=0.75
def nlp_classify(voice_string):
        """
        we want to take different actions / or routes through the application
        depending on what the user wants to do. With spoken text
        """
        # Convert to Spacy 'doc'
        utter = nlp(unicode(voice_string))
        scores = []
        cats = CLASSES
        cats_keys = cats.keys()
        # Iterate through each of the sample utterances...
        for idx,key in enumerate(cats_keys):
            v = cats[key]
            for i in v:
                # Spacy calculates the semantic similarity between
                # the user's utterance and the example utterance -
                # and gives a similarity score
                sample = nlp(unicode(i))
                sim_score = utter.similarity(sample)
                scores.append([idx,sim_score])
        # We now find the example utterance with the highest
        # similarity score, and determine its CLASS
        a = np.array(scores)
        my_cat = cats_keys[int(a[np.argmax([e for e in a[:, 1]])][0])]
        my_val = np.max([e for e in a[:, 1]])
        # if the similarity score was below THRESHOLD, then the
        # user uttered something that was not close to any of our
        # example utterances, and we treat it as an 'unknown' utterance.
        if my_val < THRESHOLD:
            my_cat = 'unknown'
        return my_cat, my_val

# takes a bit to initialize vvv.
tz = tzwhere.tzwhere()
TIME_FORMAT='%-I %M %p'

def get_time(voice_string):
    """
    get_time demos how to pull entities out of a string to use it as
    parameters - in this case, if the user specifies a city, we will
    give the local time in a city. Otherwise we'll give the local time
    where our python code is running.
    """

    # We use 'title' to capitalize all the words, entities being proper
    # nouns are capitalized. 
    doc = nlp(voice_string.title())
    print "DOC ENTS"
    print len(doc.ents)
    print "STRING"
    print voice_string
    # If an entity is detected, assume it's a specific city!
    if len(doc.ents) > 0:
        # get the city name, geocode it with Google, find the
        # timezone from the lat/lon and then get the time in that zone
        city = doc.ents[0]
        g = geocoders.GoogleV3()
        place, (lat, lng) = g.geocode(city)
        tz_str = tz.tzNameAt(lat,lng)
        c_tz = timezone(tz_str)
        now_time = datetime.now(c_tz)
        my_loc = "in %s" % city

    # Otherwise, it's just the 'local' time
    else:
        now_time = datetime.now()
        my_loc = ""

    nice_time = datetime.strftime(now_time,TIME_FORMAT)
    response = "The time %s is %s" % (my_loc, nice_time)
    return statement(response).simple_card('The Time', response) 


@ask.launch
@ask.intent('Spacy', default={'rawtext': ''})
def mainroute(rawtext=None):
    nlp_label, nlp_score = nlp_classify(rawtext)
    if nlp_label == "mood":
        r_st = "Good afternoon. Everything is going extremely well."
        return statement(r_st).simple_card('My Mood', r_st)
    elif nlp_label == 'time':
        return get_time(rawtext)
    elif nlp_label == 'unknown':
        return r_help()



if __name__ == '__main__':
    app.run()

