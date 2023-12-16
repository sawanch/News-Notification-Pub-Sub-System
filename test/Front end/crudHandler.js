// Functions created for altering and setting up events
var actions = {
    actions: {},
    alter: (action_name, fact) => {
        if (this.actions[action_name]) {
            this.actions[action_name].forEach((event) => {
                event(fact);
            });
        }
    },
    remove: (action_name) => {
        if (this.actions[action_name]) {
            this.actions[action_name].pop();
        }
    },
    setup: (action_name, event) => {
        this.actions[action_name] = this.actions[action_name] || [];
        this.actions[action_name].push(event);
    },
};
