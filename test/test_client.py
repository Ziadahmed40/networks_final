from clientoop import UDP_client_side as client

client=client("localhost",8888)
client.send_message() #client.send_message("heloo testing")
