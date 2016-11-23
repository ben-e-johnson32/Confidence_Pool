from flask import Flask, render_template, request
import nflgame
import picksdb
import random
from ast import literal_eval

app = Flask(__name__)


# The page where a user enters their pick for the week.
@app.route('/make_pick')
def make_pick():
    # TODO: Figure out scheduling (after a week's games are completed, calculate users' scores and change the week)
    # TODO: Check if the user has already entered picks for the week.

    # The week is currently hard-coded.
    week_num = 2

    # Get a list of games for the week from nflgame.
    games = nflgame.games(2016, week=week_num)

    # A list of tuples for the home and away teams.
    home_and_away = []
    for g in games:
        home = g.home
        away = g.away
        home_and_away.append((home, away))

    # Render the make_pick template with the week number and list of home and away teams.
    return render_template('make_pick.html', weekNum=week_num, games=home_and_away)


# The confirmation page appears after a user enters their picks.
@app.route('/pick_made', methods=['POST'])
def pick_made():
    # Get the week number from the form.
    weekNum = request.form['weekNum']
    games = literal_eval(request.form['games'])

    # Hard-coded userID. Apparently by default, sqlite doesn't enforce foreign key constraints, so I can add
    # a row to the picks table even if the user ID doesn't exist in the users database. Not sure if I need
    # to enable that or if I can avoid problems with good code. Currently just a random integer so I don't have to
    # change it every time I test. TODO: Implement unit tests - clicking a bunch of radio buttons all the time is lame.
    userID = random.randint(5, 1000)

    # Call read_picks on the form data to get a dictionary of the picks.
    pick_dict = read_picks(request.form)

    # Add the picks to the picks table.
    picksdb.AddPick(weekNum, userID, pick_dict)

    # TODO: Re-display the picks the user made so they can review.
    return render_template('pick_made.html', weekNum=weekNum, picks=pick_dict, games=games)


# Converts the form data into something more usable. Pretty rough draft - needs to be cleaned up.
def read_picks(form_data):
    # TODO: Make this more efficient - do I need all these different collections?

    # Three dictionaries and a list.
    data_dict = {}
    picks1 = {}
    picks2 = {}
    to_remove = []

    # Put the form data (a list of tuples) into a dictionary.
    for x in form_data:
        value = form_data[x]
        entry = {x: value}
        data_dict.update(entry)

    # Loop through the new dictionary. Each key that starts with 'conf' is the confidence value. The game number
    # is just a number. This finds each entry that is a winner pick, not a confidence value.
    for k, v in data_dict.items():
        if k[0] != 'c':
            # If it's a game pick (i.e. 'home' or 'away'), add it to the first picks dictionary and add its
            # key to the list of entries to remove from the data_dict.
            picks1.update({k: v})
            to_remove.append(k)

    # Remove all the entries we already added to the first picks dictionary.
    for k in to_remove:
        data_dict.pop(k)

    # Loop through the remaining items (the confidence values).
    for k, v in data_dict.items():
        # Strip the 'conf' off the key.
        k = k[4:]
        # p is the pick (home or away).
        p = picks1.get(k)
        # Create an entry - the key is the game number, the value is a tuple containing the pick (home or away) and the
        # confidence number.
        entry = {k: (p, v)}
        picks2.update(entry)
    return picks2


# Display the log-in page.
@app.route('/login')
def login():
    return render_template('login.html')


# The landing page after log-in. If the user exists and the password is correct, the log-in is successful.
# If not, redisplay the log-in page with a message saying the password is wrong or the user doesn't exist.
# TODO: Implement flask-login.
@app.route('/login_successful', methods=['POST'])
def login_successful():
    r = request.form
    email = r['email']
    password = r['password']
    user = picksdb.GetUser(email, password)
    if user is not None:
        return render_template('login_successful.html', user=user)
    else:
        return render_template('login.html', failed=True)


if __name__ == '__main__':
    app.run()
