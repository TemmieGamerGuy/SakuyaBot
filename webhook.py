from sanic import Sanic
from sanic.response import text
from settings import PASSWORD

app = Sanic("sakuya_post")
VOUCHERS = 1


@app.route("/webhook", methods=['POST'])
async def post_handler(request):
    print(request)
    data = request.json
    auth = request.headers["authorization"]

    if auth == PASSWORD:
        with open("vote_info.txt", "a+") as file:
            file.write(data["user"] + "," + str(VOUCHERS + VOUCHERS * data["isWeekend"]) + "\n")

    return text("recieved")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
