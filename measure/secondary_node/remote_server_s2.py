import socket
import sys
import random
from _thread import *
from threading import Timer
import time

subscribers = []
topics = ['Sports', 'Tech', 'Weather', 'Politics', 'Business']
subscribed_topics = []
subscriptions = {}
generatedEvents = dict()
flags = dict()
news = {
    'Sports': ['message'],
    'Tech':  ['message'],
    'Weather': ['message'],
    'Politics': ['message'],
    'Business': ['message']
}

currentLeader = 0

# For measurement 
numberOfEvents = [100000]
currNumberOfEventsIndex = 0
currNumberOfEvents = 0
start = 0
samples = [1]
currSamples = 0
sampleList = []

# Function to handle subscriber connection and subscription
def connect_subscriber(connection, subscriber_name, topic):
    while True:
        flags[subscriber_name] = 0
        subscribe(subscriber_name, topic)
        subscription_info = 'You are subscribing to this topic: ' + str(subscriptions[subscriber_name])
        connection.send(subscription_info.encode())

        while True:
            if flags[subscriber_name] == 1:
                notify(connection, subscriber_name)

# Function to handle middleware server sending
def middleware_server_sender(connection, server_name):
    while True:
        flags[server_name] = 0
        subscriptions[server_name] = topics
        subscription_info = 'You are subscribing to this topic: ' + str(subscriptions[server_name])
        connection.send(subscription_info.encode())

        while True:
            if flags[server_name] == 1:
                notify(connection, server_name)

# Function to handle middleware server receiving
def middleware_server_receiver(connection, server_name):
    while True:
        server_data = connection.recv(2048).decode()
        m = server_data.split('-')
        if len(m) == 2:
            topic = m[0]
            event = m[1]
            publish(topic, event, 0)

# Function to handle master sender thread
def threaded_master_sender(ss):
    while True:
        flags['master'] = 0
        subscriptions['master'] = topics
        subscription_info = 'You are subscribing to this topic: ' + str(subscriptions['master'])
        ss.send(subscription_info.encode())
        while True:
            if currentLeader == 2:
               continue 
            if flags['master'] == 1:
                notify(ss, 'master')

# Function to handle master receiver thread
def threaded_master_receiver(ss):
    while True:
        server_data = ss.recv(2048).decode()
        if server_data:
            #print("NOTIFICATION FROM MASTER:", server_data)
            p = server_data.split(' - ')
            if len(p) == 2:
                topic = p[0]
                event = p[1]
                publish(topic, event, 0)
            p = server_data.split('-')
            if len(p) == 2 and p[0] == 'leader':
                print("Received leader election message " + str(server_data))
                global currentLeader
                if int(p[1]) > currentLeader:
                    currentLeader = int(p[1])
                    ss.send(server_data.encode())
                if int(p[1]) < currentLeader:
                    msg = 'leader-' + str(currentLeader)
                    ss.send(msg.encode())
        else:
            print("Master disconnected. Election starting ...")
            currentLeader = 2
            print("No servers available. Server2 elected as a leader")
            ss.close()
            break

# Function to handle subscriber subscription
def subscribe(name, topic):
    topics = topic.split(',')
    subscriptions[name] = topics
    for t in topics:
        if t not in subscribed_topics:
            subscribed_topics.append(t)

# Function to generate random news from the given list of news
def generate_news():
    topic = random.choice(subscribed_topics)
    msg_list = news[topic]
    event = msg_list[0]
    publish(topic, event, 1)

# Function to publish news events
def publish(topic, event, indicator):
    event = topic + ' - ' + event
    if indicator == 1:
        for name, subscribed_topics in subscriptions.items():
            if topic in subscribed_topics:
                if name in generatedEvents:
                    generatedEvents[name].append(event)
                else:
                    generatedEvents.setdefault(name, []).append(event)
                flags[name] = 1
    else:
        for name, subscribed_topics in subscriptions.items():
            if name in subscribers:
                if topic in subscribed_topics:
                    if name in generatedEvents:
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    flags[name] = 1

    

# Function to notify subscribers of new events
def notify(connection, name):
    if name in generatedEvents:
        for msg in generatedEvents[name]:
            msg = msg + str("\n")
            connection.send(msg.encode())
        del generatedEvents[name]
        flags[name] = 0

    if name == subscribers[0]:
        global currNumberOfEventsIndex
        global currNumberOfEvents
        global start
        global samples
        global currSamples
        if start == 0:
            start = time.time()
        if currNumberOfEvents < numberOfEvents[currNumberOfEventsIndex]:
            currNumberOfEvents = currNumberOfEvents + 1
            generate_news()
        else:
            timeTaken = time.time() - start
            #print("Measured time: ", timeTaken)
            sampleList.append(timeTaken)
            currNumberOfEvents = 0
            start = 0
            if currSamples < samples[currNumberOfEventsIndex]:
                currSamples = currSamples + 1
                generate_news()
            else:
                print(f"Average measured time for {numberOfEvents[currNumberOfEventsIndex]} events: ", sum(sampleList)/len(sampleList))
                if currNumberOfEventsIndex < len(numberOfEvents) - 1:
                    currNumberOfEventsIndex = currNumberOfEventsIndex + 1
                    currSamples = 0
                    sampleList.clear()
                    generate_news()

# Main function
def main():
    host = ""
    port = 5041
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket is bind to the port:", port)
    s.listen(5)
    print("Socket is now listening for new connection ...")
    t = Timer(random.choice(list(range(30, 36))), generate_news)
    t.start()

    master_host = 'server1'
    master_port = 5040

    server_name = str(sys.argv[1])

    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect((master_host, master_port))

    ss.send(server_name.encode())

    start_new_thread(threaded_master_receiver, (ss,))
    start_new_thread(threaded_master_sender, (ss,))

    while True:
        connection, addr = s.accept()
        print('Connected to:', addr[0], ':', addr[1])
        data = connection.recv(2048).decode()

        if data:
            print("Welcome", data)
        l = data.split('-')
        if l[0] == 'c':
            subscribers.append(l[1])
            start_new_thread(connect_subscriber, (connection, l[1], l[2]))
        if l[0] == 's':
            start_new_thread(middleware_server_sender, (connection, l[1]))
            start_new_thread(middleware_server_receiver, (connection, l[1]))

if __name__ == '__main__':
    main()
