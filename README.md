This repo accompanies the blog post
[Using Spacy to build Conversational Interfaces for Alexa](http://www.rage.net/~greg/2018-03-20-spacy-alexa-skill.html).

Review the blog post for some setup, but basically you'll need to:

* Start w/ an Ubuntu box w/ build-essential, virtualenv, and ngrok >2.0
* install all the python packages you see in `spacy_demo.py`
* set up a demo/dev app in the alexa skill console
* Add the the correct intent schema with `AMAZON.LITERAL` slots
* start up your `ngrok` and point your skill endpoint to it
* run `python spacy_demo.py`
