import sys
import socket

def main():
    host = 'server2'
    backup_host = 'server1'
    port = 5041
    backup_port = 5040
    on_backup = False
    subscriber_name = str(sys.argv[1])
    print("Subscriber is:", subscriber_name)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
        s.send(subscriber_name.encode())
        
        while True:
            data = s.recv(2048).decode()
            if not data:
                # Server disconnected
                print("Server disconnected.")
                if on_backup:
                    break
                print("Trying to connect to backup server...")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((backup_host, backup_port))
                s.send(subscriber_name.encode())
                on_backup = True
            #print(data)

    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        s.close()

if __name__ == '__main__':
    main()
