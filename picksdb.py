import sqlite3 as lite
import os
import marshal

os.chdir(os.path.dirname(__file__))
cwd = os.getcwd()


# Script that created the picks table. The picks column is blob data - ends up being a list of tuples.
# Has a composite primary key based on the week number and user, since each user can only enter picks once
# for each week.
def CreatePicksTable():
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    cursor.execute('DROP TABLE Picks')

    cursor.execute('CREATE TABLE Picks(week INTEGER NOT NULL, user INTEGER NOT NULL, picks BLOB,'
                   'FOREIGN KEY(user) REFERENCES users(id), PRIMARY KEY (week, user))')
    db.commit()
    db.close()


# Script that created the user table. Still have to do a lot of learning on implementing user accounts,
# so I'm sure this table will change.
def CreateUserTable():
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    cursor.execute('DROP TABLE Users')

    cursor.execute('CREATE TABLE Users(id INTEGER PRIMARY KEY, username TEXT, password TEXT,'
                   'fname TEXT, lname TEXT, score INTEGER)')

    db.commit()
    db.close()


# Method to add a user.
def AddUser(username, password, fname, lname):
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    cursor.execute('INSERT INTO Users VALUES(?,?,?,?,?,?)', [None, username, password, fname, lname, 0])
    db.commit()
    db.close()


# Method to add a user's weekly picks to the picks table.
def AddPick(week, userID, pick_dict):
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    # Picks are brought in as a dictionary - this turns it into a list of tuples.
    picks = []
    for k, v in pick_dict.items():
        picks.append((k, v[0], v[1]))

    # A tuple with the data we need to add a row. Uses marshal to serialize the list of picks.
    data = (week, userID, marshal.dumps(picks))

    # Add the row.
    cursor.execute('INSERT INTO Picks VALUES(?,?,?)', data)
    db.commit()
    db.close()


# Commented-out code for testing.
# AddPick(1, 1, [('home', 1), ('home', 2), ('home', 3), ('home', 4), ('home', 5), ('home', 6), ('home', 7), ('home', 8),
#                ('home', 9), ('home', 10), ('home', 11), ('home', 12), ('home', 13), ('home', 14), ('home', 15),
#                ('home', 16)])

# db = lite.connect(cwd + '/static/confidence_pool.db')
# cursor = db.cursor()
# cursor.execute('SELECT * FROM Picks')
# row = cursor.fetchone()
# while row:
#     picks = marshal.loads(row[2])
#     print(row[0], row[1], picks)
#     row = cursor.fetchone()
# db.close()
