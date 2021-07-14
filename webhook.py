from sanic import Sanic 
from sanic.response import text
#from settings import PASSWORD, VOUCHERS

app = Sanic("sakuya_post")

PASSWORD = ""#Put password here
VOUCHERS = 1

@app.route("/webhook", methods =['POST']) 
async def on_post(request): 
	data = request.json
	auth = request.headers["authorization"]
		
	if auth == PASSWORD:
		with open("vote_info.txt","a+") as file:
			file.write(data["user"]+","+str(VOUCHERS + VOUCHERS*data["isWeekend"])+"\n")
		
	return text("recieved")
	


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000)
	