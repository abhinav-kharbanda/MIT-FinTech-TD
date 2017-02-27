from flask import Flask, render_template, request,redirect, url_for
import MySQLdb
import json
import requests

app = Flask(__name__)
 
@app.route("/", methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if (request.form['employee_name'] == "bernard.store@gmail.com" and request.form['employee_password'] == "storeGmail7@ber"):
			return render_template("status.html")

		else:
			return render_template("index.html",error=True)	
	else:
		return render_template("index.html",error=False)


#login_employee -> choose customer
@app.route("/status", methods=['GET', 'POST'])
def user_identification():
	if request.method == 'POST':
		existing = False if request.form['existing'] == 'False' else True
		return render_template("home.html", existing_customer=existing)

	else:
		return render_template("status.html")

 
@app.route("/user_login",methods=['POST'])
def user_login():
    purpose = request.form['purpose']
    name = request.form['name']
    if request.form['acc_id'] != '':
    	account_id = request.form['acc_id']
    else:
    	account_id = "NULL"

    db = MySQLdb.connect("localhost","root","qwertyuiop","fintech")
    cursor = db.cursor()
    sql = "INSERT INTO user_visit VALUES("+account_id+",'"+name+"','Bernard','"+purpose+"',NOW());"

    try:
        cursor.execute(sql) 
        db.commit()
        return form_dashboard(name,account_id,purpose)
        
    except MySQLdb.OperationalError, e:
        print sql
        print "SQL operation failed: "
        print e
        db.rollback()
        return render_template("status.html")



def form_dashboard(name,account_id,purpose):
	if account_id != "NULL":
		url = "http://52.14.11.67:8080/OBP-API-1.0/obp/v2.1.0/my/banks/td-us-bank/accounts/"+account_id+"/account"

		payload = ""
		headers = {
    				'content-type': "application/json",
    				'authorization': "DirectLogin token=\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyIiOiIifQ.Tucwqna5gGQ3W2jB3rTFdQpWd5BQ4eBQlrKWEA8cY4Q\"",
    				'cache-control': "no-cache",
    				'postman-token': "080c29a3-191d-bd3f-3a1d-e957d18409bb"
    			}

		response = requests.request("GET", url, data=payload, headers=headers)
		json_data = json.loads(response.text)

		url = "http://52.14.11.67:8080/OBP-API-1.0/obp/v2.1.0/users/current/customers"

		headers = {
    				'content-type': "application/json",
    				'authorization': "DirectLogin token=\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyIiOiIifQ.Tucwqna5gGQ3W2jB3rTFdQpWd5BQ4eBQlrKWEA8cY4Q\"",
    				'cache-control': "no-cache",
    				'postman-token': "6656de0b-5d65-ab5d-8e3d-cf6a2fc559e3"
    			}

		response2 = requests.request("GET", url, headers=headers)
		json_data2 = json.loads(response2.text)

		i=0
		for i in xrange(len(json_data2["customers"])):
			if json_data2["customers"][i]["legal_name"] == json_data['label']:
				break

		return render_template("dashboard.html",acc_id=account_id,cust_name=json_data['label'],dob=json_data2["customers"][i]["date_of_birth"],depend=json_data2["customers"][i]["dependants"],rel_status=json_data2["customers"][i]["relationship_status"],credit_rating=json_data2["customers"][i]["credit_rating"]["rating"],purpose=purpose)

	else:
		return account_id


@app.route("/credit_card_list", methods=['POST'])
def credit_card_list():

	db = MySQLdb.connect("localhost","root","qwertyuiop","fintech")
	cursor = db.cursor()
	sql = "select card_img from credit_cards order by +"+request.form['param_1']+" DESC, "+request.form['param_2']+" DESC;"

	try:
		rows_count = cursor.execute(sql) 
		if rows_count > 0:
			results = cursor.fetchall()
			return render_template("products.html",card1=results[0],card2=results[1],card3=results[2],card4=results[3],card5=results[4],card6=results[5])
		else:
			return "0"
	except MySQLdb.OperationalError, e:
		print sql
		print "SQL operation failed: "
		print e
		db.rollback()
		return form_dashboard(request.form['name'],request.form['account_id'],request.form['purpose'])

# - Cash Rewards
# - Airline Mile Rewards
# - Higher points for dining
# - Higher points for travel
# - No annual fee
# - No foreign Transaction Fee



if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080);