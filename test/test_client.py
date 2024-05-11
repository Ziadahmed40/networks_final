from clientoop import UDP_client_side as client

client=client("localhost",8888,"non-persistent")

headers = {
    "User-Agent": "MyCustomUserAgent",
    "Accept": "text/html",
    "Content-Type": "application/json"
}
# client.send_message() #client.send_message("heloo testing")
client.http_get("\\test_get",headers)
# client.http_post("\\test_get","hrjkdneijnd3eicdnen3cdiojencdijne")
# client.http_get("\\test_get")

