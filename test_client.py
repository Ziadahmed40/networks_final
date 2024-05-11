from clientoop import UDP_client_side as client

client=client("localhost",8888)
# client.send_message()
# client.send_message("heloo testing")
# client.http_get("\\test_get")
messages=["Yamen","Mohamed","Saad"]
client.stop_and_wait(messages)
