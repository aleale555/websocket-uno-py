from websockets.sync.client import connect

def main():
    print("Please enter your name: ")
    name = input ('> ')
    with connect('ws://localhost:8765') as websocket:
        websocket.send(name)
        while True:
            message = websocket.recv()
            #hangs the client til it receives a msg
            if message == '$':
                break
            elif message == '*':
                #* = ask user "its your turn to talk now"
                data = input('> ')
                websocket.send(data)
            else:
                print(message)

if __name__ == '__main__':
    main()


#fungsi synch jika disuruh wait, akan wait app-nya
#but we cant do that on the server
#hence we use asynch, while on the client, aman pakai synch