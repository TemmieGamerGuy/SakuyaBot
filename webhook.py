import sanic
from sanic import Sanic
from sanic.response import text
from settings import PASSWORD, otherpass
import requests
import sqlite3
import datetime

database = 'database.db'
conn = sqlite3.connect(database)
c = conn.cursor()

app = Sanic("sakuya_post")
VOUCHERS = 1
print(datetime.datetime.utcnow())


@app.route("/webhook", methods=['POST'])
async def post_handler(request):
    print(datetime.datetime.utcnow())
    print(request)
    data = request.json
    auth = request.headers["authorization"]
    weekend = 0
    print(data)
    if "isWeekend" in data:
        weekend = VOUCHERS * data["isWeekend"]
    if auth == PASSWORD:
        row = c.execute("SELECT * FROM vouchers WHERE userid=?", (data["user"],)).fetchone()
        if row is None:
            c.execute("INSERT INTO vouchers Values(?,?)", (data["user"], VOUCHERS + weekend))
        else:
            c.execute("UPDATE vouchers SET count=? WHERE userid=?", (row[1] + VOUCHERS + weekend, data["user"]))

        conn.commit()

    return text("recieved")


@app.route("/")
async def h(request):
    print(datetime.datetime.utcnow())
    print(request)
    data = request.json
    auth = request.headers["authorization"]
    weekend = 0
    print(data)
    if "isWeekend" in data:
        weekend = VOUCHERS * data["isWeekend"]
    if auth == PASSWORD:
        row = c.execute("SELECT * FROM vouchers WHERE userid=?", (data["user"],)).fetchone()
        if row is None:
            c.execute("INSERT INTO vouchers Values(?,?)", (data["user"], VOUCHERS + weekend))
        else:
            c.execute("UPDATE vouchers SET count=? WHERE userid=?", (row[1] + VOUCHERS + weekend, data["user"]))

        conn.commit()

    return text("recieved")


@app.route("/roblox", methods=['POST'])
async def post_handler(request: sanic.Request):
    print(request)
    data = request.body.decode("utf-8").split("!!!")
    print(data)
    print(data[1])
    auth = data[0]
    if auth == otherpass:
        tosend = {
            "content": data[1],
            "username": "Ore Tracker"
        }
        result = requests.post("https://discord.com/api/webhooks/916455003521179648/GTks8dRNJ-tt3eIFYD1ieI__rvyCwTaqY5AVP1KhZr7gWPq_e20MrwIyJPGOnrDqCGrX", json=tosend)
        print(result)
        print(result.reason)
    return text("recieved")



if __name__ == "__main__":
    app.run(host="192.168.1.150", port=5001)
