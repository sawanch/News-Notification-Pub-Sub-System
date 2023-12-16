var Subscriber = (() => {
    var list_of_subscribers = [];

    var html = $("#list-of-subscribers");
    var frame = html.html();

    //tying button clicks with actions
    html.delegate("button", "click", TopicSubscribed);

    // setup function invoked from publishsubscribe.js
    actions.setup("notify", send_to_subscriber);
    actions.setup("add_subscriber", insert);
    actions.setup("remove_subscriber", strike);

    //pushing changes to the UI
    updateChanges();

    //get subscribers from the list of subscribers
    function gets(array_position) {
        array_position = array_position || -1;
        if (array_position != -1) return list_of_subscribers[array_position];
        return list_of_subscribers;
    }

    //insert a subscriber
    function insert(name) {
        subs = list_of_subscribers.map(function (sub, array_position) {
            return sub.name.toLowerCase();
        });

        array_position = subs.indexOf(name.toLowerCase());
        if (array_position != -1) {
            alert(name + " is already present in subscriber list");
            return;
        }

        list_of_subscribers.push({ name: name });
        updateChanges();
    }

    //strikes a subscriber
    function strike(name) {
        subs = list_of_subscribers.map(function (sub, array_position) {
            return sub.name;
        });

        array_position = subs.indexOf(name);

        if (array_position != -1) {
            list_of_subscribers.splice(array_position, 1);
            updateChanges();
            return;
        }

        alert(name + " is not present in list. Please check the name again");
    }

    function updateChanges() {
        facts = {
            list_of_subscribers: list_of_subscribers,
        };
        html.html(Mustache.render(frame, facts));
    }

    function send_to_subscriber(facts) {
        list_of_subscribers.forEach(function (sub, array_position) {
            sub.TopicNames = sub.TopicNames || [];
            sub.sub_notif_list = sub.sub_notif_list || [];
            if (sub.TopicNames.indexOf(facts.TopicName) != -1)
                sub.sub_notif_list.push(facts);
        });

        updateChanges();
    }

    // to add a new topic in subscriber's subscribed list
    function TopicSubscribed(action) {
        $selected_ele = $(action.target);
        $sub = $selected_ele.closest(".subscriber");
        name = $sub.find("h5").html();
        TopicName = $sub.find("input")[0].value;

        list_of_subscribers.forEach(function (sub, array_position) {
            if (name.toLowerCase() == sub.name.toLowerCase()) {
                //initiating an empty array for topic names
                sub.TopicNames = sub.TopicNames || [];
                if (sub.TopicNames.indexOf(TopicName) == -1) {
                    sub.TopicNames.push(TopicName);
                    updateChanges();
                    return;
                }
            }
        });
    }

    return {
        gets: gets,
    };
})();

(() => {
    //getting dom objects
    var html = $("#add_rem_pub");
    // fetching the design from index.html
    var frame = html.html();

    //tying button clicks with actions
    html.delegate("button", "click", push_action);

    render();

    function push_action(action) {
        publisherName = html.find("input")[0].value;
        $selected_ele = $(action.target);
        todoInsertStrike = $selected_ele.html().toLowerCase();
        actions.alter(todoInsertStrike + "_publisher", publisherName);
        render();
    }
    //pushing changes to the UI
    function render() {
        html.find("input").val("");
    }
})();

(($) => {
    //getting dom objects
    var html = $("#add_rem_sub");

    //tying button clicks with actions
    html.delegate("button", "click", push_action);

    render();

    function push_action(action) {
        subscriberName = html.find("input")[0].value; // name of the subscriber
        $selected_ele = $(action.target);
        todoInsertStrike = $selected_ele.html().toLowerCase(); //gets the nature of operation Insert or Strike
        //incident_change =  add_subscriber | remove_subscriber
        actions.alter(todoInsertStrike + "_subscriber", subscriberName);
        render();
    }

    function render() {
        html.find("input").val("");
    }
})(jQuery); // passing jQuery for additional protection

var Publisher = (() => {
    var list_of_publishers = [];

    //getting dom objects
    var html = $("#list-of-publishers");
    var frame = html.html();

    //tying button clicks with actions
    html.delegate("button", "click", TopicPosted);

    //tying actions for publishers
    actions.setup("add_publisher", insert);
    actions.setup("remove_publisher", strike);

    updateChanges();

    //get publishers from the list of publishers
    function gets(array_position) {
        array_position = array_position || -1;
        if (array_position != -1) return list_of_publishers[array_position];
        return list_of_publishers;
    }

    //push changes to the UI
    function updateChanges() {
        facts = {
            list_of_publishers: list_of_publishers,
        };
        html.html(Mustache.render(frame, facts));
    }

    //insert a publisher.
    function insert(pub_name) {
        single_pub = list_of_publishers.map((onePublisher, array_position) => {
            return onePublisher.name.toLowerCase();
        });

        array_position = single_pub.indexOf(pub_name.toLowerCase());
        if (array_position != -1) {
            alert(pub_name + " is already present in publishers list");
            return;
        } else {
            list_of_publishers.push({ name: pub_name });
            updateChanges();
        }
    }

    //strikes a publisher.
    function strike(onePublisher) {
        single_pub = list_of_publishers.map((publisher) => {
            return publisher.name;
        });

        array_position = single_pub.indexOf(onePublisher);

        if (array_position != -1) {
            list_of_publishers.splice(array_position, 1);
            updateChanges();
            return;
        }
        alert(
            onePublisher +
                " is not present in list. Please check the name again"
        );
    }

    //post a topic and pushes to the UI
    function TopicPosted(action) {
        $selected_ele = $(action.target);
        $onePublisher = $selected_ele.closest(".publisher");
        name = $onePublisher.find("h5").html();
        TopicName = $onePublisher.find("input")[0].value;
        Details = $onePublisher.find("textarea")[0].value;

        section = {
            name: name,
            TopicName: TopicName,
            Details: Details,
        };

        single_pub = list_of_publishers.map((pub) => {
            return pub.name;
        });

        array_position = single_pub.indexOf(section.name);

        list_of_publishers[array_position].Tweets =
            list_of_publishers[array_position].Tweets || [];

        list_of_publishers[array_position].Tweets.push({
            TopicName: TopicName,
            Details: Details,
        });

        updateChanges();

        actions.alter("notify", section);
    }

    //Broadcsts the topics
    function TopicBroadcast(action) {
        $selected_ele = $(action.target);
        $onePublisher = $selected_ele.closest(".publisher");
        name = $onePublisher.find("h5").html();
        TopicName = $onePublisher.find("input")[0].value;
        Details = $onePublisher.find("textarea")[0].value;

        section = {
            name: name,
            TopicName: TopicName,
            Details: Details,
        };

        single_pub = list_of_publishers.map((pub) => {
            return pub.name;
        });

        array_position = single_pub.indexOf(section.name);

        list_of_publishers[array_position].Tweets =
            list_of_publishers[array_position].Tweets || [];

        list_of_publishers[array_position].Tweets.push({
            TopicName: TopicName,
            Details: Details,
        });

        updateChanges();

        actions.alter("notify", section);
    }

    return {
        gets: gets,
        TopicPosted: TopicPosted,
    };
})();
