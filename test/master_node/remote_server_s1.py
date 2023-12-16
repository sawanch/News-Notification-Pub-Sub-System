import socket
import random
from _thread import *
from threading import Timer

# List to store subscribers' names
subscribers = []
# Available topics
topics = ['Sports', 'Tech', 'Weather', 'Politics', 'Business']
subscribed_topics = []
# Dictionary to store subscriptions of each subscriber
subscriptions = {}
# Dictionary to store news for each topic
news = {
    'Sports': ['Australia won the 2023 cricket world cup', 'Chris Paul, Draymond Green top sport rivals turned teammates'],
    'Tech': ['OpenAI Board sacks Sam Altman as CEO', 'Sam Altman returns as CEO of OpenAI in dramatic turn of events'],
    'Weather': ['After Rain and Snow in the Eastern U.S., Weather Clears for Thanksgiving', 'Alaska landslide leaves at least 3 dead'],
    'Politics': ['Political Pressures on Biden Helped Drive Secret Cell of Aides in Hostage Talks', 'The Only Thing Worse Than the Ron DeSantis–Gavin Newsom Debate Is Its Moderator'],
    'Business': ['Jake Tapper reveals challenges of covering war, why he feels news outlets censor too much and what has left him shocked', 'Luis Cubel promoted to Arla Foods Ingredients CEO']
}

# Variables for leader election
currentLeader = 1
firstTime = 0

# Dictionary to store generated events for each subscriber
generatedEvents = dict()

# Dictionary to indicate if a subscriber has new events
flags = dict()

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
        global firstTime
        if firstTime == 0:
            msg = "leader-1"
            print("Initiating leader election message " + str(msg))
            connection.send(msg.encode())
            firstTime = 1
        while True:
            if flags[server_name] == 1:
                notify(connection, server_name)

# Function to handle middleware server receiving
def middleware_server_receiver(connection, server_name):
    while True:
        server_data = connection.recv(2048).decode()
        m = server_data.split('-')
        if len(m) == 2:
            if m[0] == 'leader':
                print("Received leader election message " + str(server_data))
                global currentLeader
                if int(m[1]) > currentLeader:
                    currentLeader = int(m[1])
                    connection.send(server_data.encode())
                if int(m[1]) == currentLeader:
                    print("Server1 elected as a leader")
            else:
                topic = m[0]
                event = m[1]
                publish(topic, event, 0)

# Function to handle subscriber subscription
def subscribe(name, topic):
    topics = topic.split(',')
    subscriptions[name] = topics
    for t in topics:
        if t not in subscribed_topics:
            subscribed_topics.append(t)


# Function to generate and publish news events
def generate_news():
    topic = random.choice(subscribed_topics)
    msg_list = news[topic]
    event = msg_list[random.choice(list(range(1, len(msg_list))))]

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
            if name in subscribers:  # only for clients
                if topic in subscribed_topics:
                    if name in generatedEvents:
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    flags[name] = 1

    t = Timer(random.choice(list(range(5, 10))), generate_news)
    t.start()

# Function to notify subscribers of new events
def notify(connection, name):
    if name in generatedEvents:
        for msg in generatedEvents[name]:
            msg = msg + str("\n")
            connection.send(msg.encode())
        del generatedEvents[name]
        flags[name] = 0

# Main function
def main():
    host = ""
    port = 5040
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket is bind to the port:", port)
    s.listen(5)
    print("Socket is now listening for new connections ...")

    t = Timer(random.choice(list(range(20, 26))), generate_news)
    t.start()

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
