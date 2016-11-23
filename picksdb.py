from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, TypeDecorator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3 as lite
import os
import marshal

os.chdir(os.path.dirname(__file__))
cwd = os.getcwd()
engine = create_engine('sqlite:////' + cwd + '/static/confidence_pool.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)


# Attempt at making my own SQLAlchemy type so I can store the lists of picks.
class SQList(TypeDecorator):
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            return marshal.dumps(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return marshal.loads(value)


# SQLAlchemy Pick class.
class Pick(Base):
    __tablename__ = "Picks"
    week = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey('Users.email'), primary_key=True)
    picks = Column(SQList)


# SQLAlchemy User class.
class User(Base):
    __tablename__ = "Users"
    email = Column(String, primary_key=True)
    username = Column(String)
    password = Column(String)
    fname = Column(String)
    lname = Column(String)
    score = Column(Integer)

    def __init__(self, email, username, password, fname, lname, score):
        self.email = email
        self.username = username
        self.password = password
        self.fname = fname
        self.lname = lname
        self.score = score


# A method to get a user from the Users table. Currently very insecure - just a start.
# TODO: Implement flask-login.
def GetUser(email, password):
    session = Session()
    user = session.query(User).filter(User.email == email).first()
    session.close()
    if password == user.password:
        return user
    else:
        return None


# Script that created the picks table. The picks column is blob data - ends up being a list of tuples.
# Has a composite primary key based on the week number and user, since each user can only enter picks once
# for each week.
def CreatePicksTable():
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    cursor.execute('DROP TABLE Picks')

    cursor.execute('CREATE TABLE Picks(week INTEGER NOT NULL, user_email TEXT NOT NULL, picks BLOB,'
                   'FOREIGN KEY(user_email) REFERENCES users(email), PRIMARY KEY (week, user_email))')
    db.commit()
    db.close()


# Script that created the user table. Still have to do a lot of learning on implementing user accounts,
# so I'm sure this table will change.
def CreateUserTable():
    db = lite.connect(cwd + '/static/confidence_pool.db')
    cursor = db.cursor()

    cursor.execute('DROP TABLE Users')

    cursor.execute('CREATE TABLE Users(email TEXT PRIMARY KEY, username TEXT, password TEXT,'
                   'fname TEXT, lname TEXT, score INTEGER)')

    db.commit()
    db.close()


# Method to add a user.
def AddUser(user):
    session = Session()
    session.add(user)
    session.commit()
    session.close()


# Method to add a user's weekly picks to the picks table.
# TODO: Clean-up old, commented out code.
def AddPick(week, user_email, pick_dict):
    session = Session()
    # db = lite.connect(cwd + '/static/confidence_pool.db')
    # cursor = db.cursor()

    # Picks are brought in as a dictionary - this turns it into a list of tuples.
    picks = []
    for k, v in pick_dict.items():
        picks.append((k, v[0], v[1]))

    pick = Pick(week, user_email, picks)
    session.add(pick)
    session.commit()
    session.close()

    # # A tuple with the data we need to add a row. Uses marshal to serialize the list of picks.
    # data = (week, user_email, marshal.dumps(picks))
    #
    # # Add the row.
    # cursor.execute('INSERT INTO Picks VALUES(?,?,?)', data)
    # db.commit()
    # db.close()


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

# user = User('abc@123.com', 'admin', 'abc123', 'Ben', 'Johnson', 0)
# AddUser(user)
