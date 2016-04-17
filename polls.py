from flask import Flask, request, render_template, abort
from flask.ext.shelve import get_shelve, init_app
import datetime as dt

app = Flask(__name__)
app.config.from_envvar('FLASK_SETTINGS')
init_app(app)


class Poll:

    def __init__(self, title, choices):
        self.created = dt.datetime.now()
        self.title = title
        self.choices = choices
        self.responses = []

    def register(self, response):
        self.responses.append(response)

    def vote_count(self):
        return {c: sum(x.votes[c] for x in self.responses) for c in self.choices}


class Response:

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment
        self.votes = {}

    def cast(self, choice, selected):
        self.votes[choice] = selected


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_shelve('c')
    polls = db.get('polls', [])
    if request.method == 'POST':
        title = request.form['title']
        choices = set(x for x in request.form['choices'].splitlines() if x)
        polls.append(Poll(title, choices))
        db['polls'] = polls
    return render_template('index.html', polls=polls)


@app.route('/<index>', methods=['GET', 'POST'])
def poll(index):
    db = get_shelve('c')
    polls = db.get('polls', [])
    try:
        poll = polls[int(index)]
    except:
        abort(404)
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        response = Response(name, comment)
        for choice in poll.choices:
            selected = request.form.get(choice) == 'on'
            response.cast(choice, selected)
        poll.register(response)
        polls[int(index)] = poll
        db['polls'] = polls
    counts = poll.vote_count()
    return render_template('poll.html', poll=poll, index=index, counts=counts)


if __name__ == '__main__':
    app.run(debug=True)
