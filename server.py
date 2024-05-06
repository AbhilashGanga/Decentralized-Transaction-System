
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
import click
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, url_for
from convertor import convert_crypto, convert_currency
import numpy as np
import random
import string
from datetime import datetime


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://hs3447:567690@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

gUserProfile = {}
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    conn.close()
  except Exception as e:
    pass



@app.route('/', methods = ['GET','POST'])
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  if request.method == "POST":
    return redirect(url_for('landing'))
  else:
    return render_template("login.html",zip = zip)


@app.route('/landing')
def landing():
  return render_template('index.html', **gUserProfile, zip = zip)


@app.route('/add_assets')
def add_assets():
  return render_template('add_assets.html',**gUserProfile, zip = zip)


@app.route('/processAssetAddition', methods = ['POST'])
def processAssetAddition():
  form = request.form.to_dict()
  print(form)
  try:
    transfer_type = form['transferType']
  except:
    return render_template("incorrect-assetAddition.html", zip = zip)

  if transfer_type == "digitalCurrency":
    try:
      currency_type = form["digitalCurrency"]
    except:
      return render_template("incorrect-assetAddition.html", zip = zip)
    
    amount = form['amount']
    sql_request  = "SELECT dc.assetId, dc.amount FROM DigitalCurrency dc WHERE dc.userID=:userid AND dc.type=:type"
    params = {
      'userid': gUserProfile['userID'],
      'type': currency_type
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    if len(amount) == 0 or float(amount) <= 0:
      return render_template("incorrect-assetAddition.html", zip = zip)

    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
    print(data)
    try:
      params['amount'] = float(amount) + float(data['amount'])
      params['assetid'] = data['assetID']
      print(params)
      sql_request = "UPDATE digitalcurrency SET amount=:amount, since=:since WHERE assetid=:assetid AND userid=:userid"
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from try")
      print(params)
    except:
      params['assetid'] = random.randint(1, 2**31 - 1)
      params['name'] = generate_random_alphanumeric_string(10)
      params['amount'] = float(amount)

      sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
        VALUES (:assetid, :amount, :name, :userid, :since)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()

      sql_request = """INSERT INTO digitalcurrency (assetID, amount, name, userID, since, type)
        VALUES (:assetid, :amount, :name, :userid, :since, :type)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from except")
      print(params)
  
  elif transfer_type == "currency":
    try:
      currency_type = form["currency"]
    except:
      return render_template("incorrect-assetAddition.html", zip = zip)
    
    amount = form['amount']
    sql_request  = "SELECT dc.assetId, dc.amount FROM currency dc WHERE dc.userID=:userid AND dc.denomination=:type"
    params = {
      'userid': gUserProfile['userID'],
      'type': currency_type
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    if len(amount) == 0 or float(amount) <= 0:
      return render_template("incorrect-assetAddition.html", zip = zip)

    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
    print(data)
    try:
      params['amount'] = float(data['amount']) + float(amount)
      params['assetID'] = data['assetID']

      print(params)
      sql_request = "UPDATE currency SET amount=:amount, since=:since WHERE assetid=:assetID AND userid=:userid"
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from try")
      print(params)
    except:

      params['amount'] = float(amount)
      params['assetid'] = random.randint(1, 2**31 - 1)
      params['name'] = generate_random_alphanumeric_string(10)

      sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
        VALUES (:assetid, :amount, :name, :userid, :since)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()

      sql_request = """INSERT INTO currency (assetID, amount, name, userID, since, denomination)
        VALUES (:assetid, :amount, :name, :userid, :since, :type)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from except")
      print(params)
  
  else:
    try:
      amount = form["assetValue"]
    except:
      return render_template("incorrect-assetAddition.html", zip = zip)
    
    if len(amount) == 0 or float(amount) <= 0:
      return render_template("incorrect-assetAddition.html", zip = zip)

    params = {}
    params['amount'] = amount
    params['userid'] = gUserProfile['userID']
    params['assetID'] = random.randint(1, 2**31 - 1)
    params['name'] = generate_random_alphanumeric_string(10)
    params['type'] = "tinyurl.com/"+generate_random_alphanumeric_string(7)
    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]

    sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
      VALUES (:assetID, :amount, :name, :userid, :since)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params)
    conn.commit()

    sql_request = """INSERT INTO digitalasset (assetID, amount, name, userID, since, location)
      VALUES (:assetID, :amount, :name, :userid, :since, :type)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params)
    conn.commit()
    print(params)    

  collect()
  return render_template('index.html',**gUserProfile, zip = zip)


@app.route('/collect')
def collect():

  global gUserProfile
  print(gUserProfile)
  # Check whether the user is a miner or not
  # Get Basic Info of the user
  sql_request = "SELECT * FROM miner WHERE miner.userID=:userid"
  params = {
    'userid': gUserProfile['userID']
  }
  conn = engine.connect()
  cursor = conn.execute(text(sql_request), params)
  conn.commit()

  ct = 0
  for result in cursor:
    ct += 1
  
  if ct == 0:
    gUserProfile['miner'] = 0
  else:
    gUserProfile['miner'] = 1
    netReward = 0
    sql_query = "SELECT * FROM gains_reward_relays_reward m WHERE m.userID=:userid"
    # sql_query = """
    # SELECT distinct GR.rid, GR.blockid, GR.amount, GR.denomination, p.nodeid, n.mac_address
    # FROM Gains_Reward_Relays_Reward GR
    # JOIN Block_ConnectedTo BC ON GR.BlockID = BC.BlockID_From
    # JOIN Miner M ON M.userid = GR.userid JOIN controls c on c.userid = m.userid JOIN performs p on c.nodeid = p.nodeid JOIN node n on n.nodeid = p.nodeid where gr.userid = :userid and c.usertype = 1 ;
    # """
    conn = engine.connect()
    params = {
      'userid': gUserProfile['userID']
    }
    cursor = conn.execute(text(sql_query), params)
    conn.commit()

    rids = []
    ramts = []
    rtypes = []
    rblocks = []
    rnodes = []
    rmacs = []
    for result in cursor:
      rids.append(result[2])
      rblocks.append(result[1])
      ramts.append(result[3])
      rtypes.append(result[4])
      # rnodes.append(result[4])
      # rmacs.append(result[5])

    gUserProfile['rids'] = rids
    gUserProfile['ramts'] = ramts
    gUserProfile['rtypes'] = rtypes
    gUserProfile['rblocks'] = rblocks
    gUserProfile['rnodes'] = rnodes
    gUserProfile['rmacs'] = rmacs

    netReward = sum(gUserProfile['ramts'])
    gUserProfile['netReward'] = round(netReward,2)

  # Get Digital Currency Details Owned By the User
  sql_request = "SELECT dc.assetId, dc.amount, dc.since, dc.type FROM DigitalCurrency dc WHERE dc.userID=:userid ORDER BY since DESC"
  conn = engine.connect()
  params = {
    'userid':gUserProfile['userID']
  }
  cursor = conn.execute(text(sql_request), params)
  conn.commit()

  digCurAssetIDs = []
  digCurValuations = []
  digCurDates = []
  digCurTypes = []
  for result in cursor:
    digCurAssetIDs.append(result[0])
    digCurValuations.append(round(float(result[1]),4))
    digCurDates.append(result[2])
    digCurTypes.append(result[3])
  
  gUserProfile['digCurAssetIDs'] = digCurAssetIDs
  gUserProfile['digCurValuations'] = digCurValuations
  gUserProfile['digCurTypes'] = digCurTypes
  gUserProfile['digCurDates'] = digCurDates


  # Get Digital Assets of a user
  sql_request = "SELECT da.assetId, da.location, da.amount, da.since FROM DigitalAsset da WHERE da.userID=:userid ORDER BY since DESC"
  conn = engine.connect()
  cursor = conn.execute(text(sql_request),params)
  conn.commit()

  digAssetIDs = []
  digValuations = []
  digDates = []
  digLocations = []

  for result in cursor:
    digAssetIDs.append(result[0])
    digLocations.append(result[1])
    digValuations.append(round(float(result[2]),4))
    digDates.append(result[3])
  
  gUserProfile['digAssetIDs'] = digAssetIDs
  gUserProfile['digValuations'] = digValuations
  gUserProfile['digLocations'] = digLocations
  gUserProfile['digDates'] = digDates

    # Get Currency Details Owned By the User
  sql_request = "SELECT c.assetId, c.denomination, c.amount FROM currency c WHERE c.userID=:userid ORDER BY since DESC"
  conn = engine.connect()
  cursor = conn.execute(text(sql_request), params)
  conn.commit()

  curAssetIDs = []
  curValuations = []
  curTypes = []

  for result in cursor:
    curValuations.append(round(float(result[2]),4))
    curTypes.append(result[1])
    curAssetIDs.append(result[0])
  
  gUserProfile['curAssetIDs'] = curAssetIDs
  gUserProfile['curValuations'] = curValuations
  gUserProfile['curTypes'] = curTypes


  # Getting the USD values for all valuations 
  netCurrency , netDigCurrency , netAsset = 0,0, sum(digValuations)
  for i,amt in enumerate(digCurValuations):
    netDigCurrency += convert_crypto(digCurTypes[i],amt)
  
  for i,amt in enumerate(curValuations):
    netCurrency += convert_currency(curTypes[i], amt)
  
  gUserProfile['netCurrency'] = round(netCurrency,2)
  gUserProfile['netDigCurrency'] = round(netDigCurrency,2)
  gUserProfile['netAsset'] = round(netAsset,2)
  



  return render_template("index.html", **gUserProfile, zip = zip)


@app.route('/add_user', methods = ['POST'])
def add_user():
    userForm = request.form.to_dict()
    print(userForm)
    name = userForm['First Name']+' '+userForm['Last Name']
    userid = userForm['userid']
    username = userForm['username']
    userType = userForm['userType']

    sql_request = """INSERT INTO users (userid, username, name) VALUES (:userid,:username,:name)"""
    conn = engine.connect()
    params = {
      'userid':userid, 
      'username':username,
      'name':name
    }
    
    try:
      cursor = conn.execute(text(sql_request), params)
      conn.commit()
      gUserProfile['userID'] = userid
      gUserProfile['name'] = name

      if userType == "Miner":
        params['power'] = random.uniform(0,1)
        gUserProfile['miner'] = 1
        sql_request = """INSERT INTO miner (userid, username, name, power) VALUES (:userid,:username,:name,:power)"""
        conn = engine.connect()
        cursor = conn.execute(text(sql_request), params)
        conn.commit()

      return redirect('collect')
    
    except:
      return render_template('incorrect_user.html', zip = zip)


@app.route('/login', methods=['GET','POST'])
def login():
  global gUserProfile

  if request.method == 'POST':

    gUserProfile = {}

    user = request.form['userID']

   # Get Basic Info of the user
    sql_request = "SELECT * FROM Users WHERE users.userID=:userid"
    params = {
      'userid': user
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    ct = 0
    for result in cursor:
      ct += 1
      gUserProfile['name'] = result[2]
      gUserProfile['userID'] = result[0]
    


    if ct == 0:
      return render_template("incorrect_login.html", zip = zip)
    else:
      return redirect(url_for('collect'))
  else:
    return redirect('/')


@app.route('/rewards')
def rewards():
  return render_template('rewards.html', **gUserProfile, zip = zip)


@app.route('/register', methods=['GET','POST'])
def register():
  return render_template("register.html", zip = zip)


@app.route('/digital_currency')
def digital_currency():
  return render_template("digital-currency.html", **gUserProfile,  zip = zip)


@app.route('/currency')
def currency():
  return render_template("currency.html", **gUserProfile,  zip = zip)


@app.route('/digital_asset')
def digital_asset():
  return render_template("digital-assets.html", **gUserProfile,  zip = zip)

@app.route('/transaction')
def transaction():
  return render_template('transaction.html',**gUserProfile,  zip = zip)


def create_user_entry(user1, user2):
  sql_request = "SELECT * FROM Completes WHERE Completes.userID1=:userid1 AND Completes.userID2=:userid2"
  params = {
    'userid1': user1,
    'userid2': user2
  }
  conn = engine.connect()
  try:
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
  except:
    return -1
  
  receiver_data = {}
  for result in cursor:
    receiver_data['user1'] = result[0]
    receiver_data['user2'] = result[1]

  if len(receiver_data) == 0:
    sql_request = """INSERT INTO Completes (UserID1, UserID2) VALUES (:userid1,:userid2)"""
    conn = engine.connect()
    try:
      print("Inserted")
      cursor = conn.execute(text(sql_request), params)
      conn.commit()
    except:
      return -1 
  return 0

def generate_random_alphanumeric_string(length):
    characters = string.ascii_letters + string.digits
    random_alphanumeric_string = ''.join(random.choice(characters) for _ in range(length))
    return random_alphanumeric_string

def create_transaction_details(user1, user2, amount, type):
  params = {}
  params['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  params['tid'] = generate_random_alphanumeric_string(30)
  params['tHash'] = generate_random_alphanumeric_string(60)
  params['userid1'] = user1
  params['userid2'] = user2
  params['amount'] = amount
  params['type'] = type

  sql_request = "SELECT b.blockid_from FROM Block_connectedto b ORDER BY random() LIMIT 1"
  conn = engine.connect()
  cursor = conn.execute(text(sql_request))
  conn.commit()
  
  for result in cursor:
    params['blockid'] = result[0]
  
  
  sql_request = """INSERT INTO Execute_transaction_storedin (UserID1, UserID2, BlockID, tID, time, tHash, amount, type)
    VALUES (:userid1, :userid2, :blockid, :tid, :time, :tHash, :amount, :type)"""
  
  while(1):
    try:
      print(params)
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      break
    except:
      params['tid'] = generate_random_alphanumeric_string(30)
      params['tHash'] = generate_random_alphanumeric_string(60)
  
  params_performs = {}
  params_performs['tid'] = params['tid']
  params_performs['time'] = params['time']

  sql_request = "SELECT n.nodeid FROM node n ORDER BY random() LIMIT 2"
  conn = engine.connect()
  cursor = conn.execute(text(sql_request))
  conn.commit()
  
  datas = []
  for result in cursor:
    datas.append(result[0])
  
  for data in datas:
    sql_request = """INSERT INTO Performs (tID, NodeID, time) VALUES (:tid, :nodeid, :time)"""
    params_performs['nodeid'] = data
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_performs)
    conn.commit()

  params_controls = {}
  params_controls['tid'] = params['tid']
  params_controls['userid'] = params['userid1']
  params_controls['nodeid'] = datas[0]
  params_controls['usertype'] = 0

  sql_request = """INSERT INTO Controls (userID, tID, NodeID, usertype) VALUES (:userid, :tid, :nodeid, :usertype)"""
  conn = engine.connect()
  cursor = conn.execute(text(sql_request),params_controls)
  conn.commit()
  
  params_controls['nodeid'] = datas[1]
  params_controls['usertype'] = 1

  sql_request = "SELECT m.userid, m.power FROM miner m"
  conn = engine.connect()
  cursor = conn.execute(text(sql_request))
  conn.commit()

  data_miner_details = []
  data_miner_probab = []
  sum = 0
  for result in cursor:
    data_miner_details.append(result[0])
    data_miner_probab.append(float(result[1]))
    sum += float(result[1])

  data_miner_details = np.array(data_miner_details)
  data_miner_probab = np.array(data_miner_probab)
  data_miner_probab /= sum
  random_event = np.random.choice(data_miner_details, size=1, p=data_miner_probab)
  
  params_controls['userid'] = random_event[0]
  print("miner",params_controls)
  
  try:
    sql_request = """INSERT INTO Controls (userID, tID, NodeID, usertype) VALUES (:userid, :tid, :nodeid, :usertype)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_controls)
    conn.commit()
  except:
    sql_request = "SELECT m.userid FROM miner m ORDER BY random() LIMIT 1"
    conn = engine.connect()
    cursor = conn.execute(text(sql_request))
    conn.commit()
    for result in cursor:
      params_controls['userid'] = result[0]
  
  params_rewards = {}
  params_rewards['userid'] = params_controls['userid']
  params_rewards['blockid'] = params['blockid']
  params_rewards['rewardid'] = random.randint(1, 2**31 - 1)
  params_rewards['amount'] = random_float_range = random.uniform(0,1)
  params_rewards['denomination'] = "USD"

  try:
    sql_request = """INSERT INTO Gains_Reward_Relays_Reward (userID, BlockID, rID, amount, denomination)
      VALUES (:userid, :blockid, :rewardid, :amount, :denomination)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_rewards)
    conn.commit()
  except:
    params_rewards['rewardid'] = random.randint(1, 2**31 - 1)
  
  sql_request = "SELECT * FROM currency c where c.denomination=:denomination AND userid=:userid"
  par = {
    "denomination": "USD",
    "userid": params_controls['userid']
  }
  conn = engine.connect()
  cursor = conn.execute(text(sql_request),par)
  conn.commit()
  
  data = {}
  for result in cursor:
    data['assetid'] = result[0]
    data['amount'] = result[1]

  print(data)
  try:
    params_add_money = {}
    params_add_money['userid'] = params_controls['userid']
    params_add_money['amount'] = float(params_rewards['amount']) + float(data['amount'])
    params_add_money['assetid'] = data['assetid']
    params_add_money['since'] = params['time'].split()[0]

    sql_request = "UPDATE currency SET amount=:amount, since=:since WHERE assetid=:assetid AND userid=:userid"
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_add_money)
    conn.commit()
    print("In try")
    print(params_add_money)
  except:
    params_add_money = {}
    params_add_money['userid'] = params_controls['userid']
    params_add_money['amount'] = float(params_rewards['amount'])
    params_add_money['assetid'] = random.randint(1, 2**31 - 1)
    params_add_money['since'] = params['time'].split()[0]
    params_add_money['denomination'] = "USD"
    params_add_money['name'] = generate_random_alphanumeric_string(10)

    sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
      VALUES (:assetid, :amount, :name, :userid, :since)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_add_money)
    conn.commit()
    
    sql_request = """INSERT INTO currency (assetID, amount, name, userID, since, denomination)
      VALUES (:assetid, :amount, :name, :userid, :since, :denomination)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params_add_money)
    conn.commit()
    print("In except")
    print(params_add_money)


@app.route('/processTransaction', methods = ['POST'])
def processTransaction():
  form = request.form.to_dict()
  print(form)
  receiver = form['userID']

  sql_request = "SELECT * FROM Users WHERE users.userID=:userid"
  params = {
    'userid': receiver
  }
  conn = engine.connect()
  cursor = conn.execute(text(sql_request), params)
  conn.commit()
  
  receiver_data = {}
  for result in cursor:
    receiver_data['name'] = result[2]
    receiver_data['userID'] = result[0]

  if len(receiver_data) == 0:
    return render_template("incorrect_transaction.html", zip = zip)

  try:
    transfer_type = form['transferType']
  except:
    return render_template("incorrect_transaction.html", zip = zip )

  if transfer_type == "digitalCurrency":
    try:
      currency_type = form["digitalCurrency"]
    except:
      return render_template("incorrect_transaction.html", zip = zip)
    
    amount = form['amount']
    sql_request  = "SELECT dc.assetId, dc.amount FROM DigitalCurrency dc WHERE dc.userID=:userid AND dc.type=:type"
    params = {
      'userid': gUserProfile['userID'],
      'type': currency_type
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    if len(amount) == 0 or float(amount) <= 0:
      return render_template("incorrect_transaction.html", zip = zip)
    
    print(float(data['amount']))
    print(float(amount))
    print("value is ",float(data['amount']) < float(amount))
    if float(data['amount']) < float(amount):
      return render_template("incorrect_transaction.html", zip = zip)
    
    if create_user_entry(gUserProfile['userID'],receiver) == -1:
      return render_template("incorrect_transaction.html", zip = zip)
    
    create_transaction_details(gUserProfile['userID'],receiver,amount,currency_type)

    sql_request = "UPDATE DigitalCurrency SET amount=:amount, since=:since WHERE userid=:userid AND assetid=:assetID"
    params['amount'] = float(data['amount']) - float(amount)
    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
    params['assetID'] = data['assetID']
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    print("From here")
    print(params)

    sql_request  = "SELECT dc.assetId, dc.amount FROM DigitalCurrency dc WHERE dc.userID=:userid AND dc.type=:type"
    params['userid'] = receiver_data['userID']
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    print(data)
    try:
      params['amount'] = float(data['amount']) + float(amount)
      params['assetid'] = data['assetID']

      print(params)
      sql_request = "UPDATE digitalcurrency SET amount=:amount, since=:since WHERE assetid=:assetid AND userid=:userid"
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from try")
      print(params)
    except:

      params['amount'] = float(amount)
      params['assetid'] = random.randint(1, 2**31 - 1)
      params['name'] = generate_random_alphanumeric_string(10)

      sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
        VALUES (:assetid, :amount, :name, :userid, :since)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()

      sql_request = """INSERT INTO digitalcurrency (assetID, amount, name, userID, since, type)
        VALUES (:assetid, :amount, :name, :userid, :since, :type)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from except")
      print(params)


  elif transfer_type == "currency":
    try:
      currency_type = form["currency"]
    except:
      return render_template("incorrect_transaction.html", zip = zip)
    
    amount = form['amount']
    sql_request  = "SELECT dc.assetId, dc.amount FROM currency dc WHERE dc.userID=:userid AND dc.denomination=:type"
    params = {
      'userid': gUserProfile['userID'],
      'type': currency_type
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    if len(amount) == 0 or float(amount) <= 0:
      return render_template("incorrect_transaction.html", zip = zip)
    
    print(float(data['amount']))
    print(float(amount))
    if float(data['amount']) < float(amount):
      return render_template("incorrect_transaction.html", zip = zip)
    
    if create_user_entry(gUserProfile['userID'],receiver) == -1:
      return render_template("incorrect_transaction.html", zip = zip)
    
    create_transaction_details(gUserProfile['userID'],receiver,amount,currency_type)

    sql_request = "UPDATE currency SET amount=:amount, since=:since WHERE userid=:userid AND assetid=:assetID"
    params['amount'] = float(data['amount']) - float(amount)
    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
    params['assetID'] = data['assetID']
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    print("From here")
    print(params)

    sql_request  = "SELECT dc.assetId, dc.amount FROM currency dc WHERE dc.userID=:userid AND dc.denomination=:type"
    params['userid'] = receiver_data['userID']
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]

    print(data)
    try:
      params['amount'] = float(data['amount']) + float(amount)
      params['assetid'] = data['assetID']

      print(params)
      sql_request = "UPDATE currency SET amount=:amount, since=:since WHERE assetid=:assetid AND userid=:userid"
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from try")
      print(params)
    except:

      params['amount'] = float(amount)
      params['assetid'] = random.randint(1, 2**31 - 1)
      params['name'] = generate_random_alphanumeric_string(10)

      sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
        VALUES (:assetid, :amount, :name, :userid, :since)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()

      sql_request = """INSERT INTO currency (assetID, amount, name, userID, since, denomination)
        VALUES (:assetid, :amount, :name, :userid, :since, :type)"""
      conn = engine.connect()
      cursor = conn.execute(text(sql_request),params)
      conn.commit()
      print("from except")
      print(params)


  else:
    try:
      currency_type = form["asset"]
    except:
      return render_template("incorrect_transaction.html", zip = zip )
    
    sql_request  = "SELECT dc.assetId, dc.amount, dc.location FROM digitalasset dc WHERE dc.userID=:userid AND dc.assetid=:type"
    params = {
      'userid': gUserProfile['userID'],
      'type': currency_type
    }
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    
    data = {}
    for result in cursor:
      data['amount'] = result[1]
      data['assetID'] = result[0]
      data['location'] = result[2]
    
    if create_user_entry(gUserProfile['userID'],receiver) == -1:
      return render_template("incorrect_transaction.html", zip = zip )
    
    create_transaction_details(gUserProfile['userID'],receiver,data['amount'],currency_type)

    sql_request = "DELETE FROM digitalAsset WHERE userid=:userid AND assetid=:assetID"
    params['since'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
    params['assetID'] = data['assetID']
    conn = engine.connect()
    cursor = conn.execute(text(sql_request), params)
    conn.commit()
    print("From here")
    print(params)

    params['amount'] = data['amount']
    params['name'] = generate_random_alphanumeric_string(10)
    params['userid'] = receiver_data['userID']
    params['type'] = data['location']

    sql_request = """INSERT INTO asset_ownedby (assetID, amount, name, userID, since)
      VALUES (:assetID, :amount, :name, :userid, :since)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params)
    conn.commit()

    sql_request = """INSERT INTO digitalasset (assetID, amount, name, userID, since, location)
      VALUES (:assetID, :amount, :name, :userid, :since, :type)"""
    conn = engine.connect()
    cursor = conn.execute(text(sql_request),params)
    conn.commit()
    print(params)    

  print(gUserProfile)
  collect()
  return redirect('/landing')


@app.route('/incoming_transactions')
def incoming_transactions():
  return render_template('incoming_transactions.html', **gUserProfile, zip = zip)

@app.route('/outgoing_transactions')
def outgoing_transactions():
  return render_template('outgoing_transactions.html', **gUserProfile, zip = zip )


@app.route('/history')
def history():
  #sql_request = "SELECT * FROM execute_transaction_storedin ex WHERE ex.userid1=:userid1 or ex.userid2=:userid2 ORDER BY time DESC"
  sql_request = """ SELECT ex.userid1, ex.userid2, ex.tid, n.ip_address, ex.type, ex.amount 
    FROM execute_transaction_storedin ex, node n, controls c
    WHERE (ex.userid1=:userid1 OR ex.userid2=:userid2) AND c.userid = ex.userid1 AND c.usertype = 0 AND c.tid = ex.tid and n.nodeid = c.nodeid 
    ORDER BY ex.time DESC
  """
  params = {
      'userid1': gUserProfile['userID'],
      'userid2': gUserProfile['userID']
  }
  conn = engine.connect()
  cursor = conn.execute(text(sql_request), params)
  conn.commit()

  incoming_transfers = []
  outgoing_transfers = []
  transfers = []

  for result in cursor:

    print(result)
    sender = result[0]
    reciever = result[1]
    tID = result[2]
    amount = result[-1]
    tp = result[-2]
    ip = result[3]

    if sender == gUserProfile['userID']:
      outgoing_transfers.append((sender, reciever, tID, amount, tp, ip))
    else:
      incoming_transfers.append((sender, reciever, tID, amount, tp, ip))
    
    transfers.append((sender, reciever, tID, amount, tp, ip))

  gUserProfile['incomingTransfers'] = incoming_transfers
  gUserProfile['outgoingTransfers'] = outgoing_transfers
  gUserProfile['transfers'] = transfers

  return render_template('history.html', **gUserProfile, zip = zip)


if __name__ == "__main__":


  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    app.jinja_env.globals.update(zip=zip)
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
