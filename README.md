## Meet Q

Q is your 21st century slack bot. He uses API Gateway and Lambda along with Slack Event Subscriptions and webhooks to help you and all of your friends do cool things. 

### Getting Help From Q

Q Works by slack event subscriptions. When a channel sends a subscription event to the API gateway endpoint specified, Lambda reads the input from slack and parses out the text. If the response begins with `!` then the bot processes the command. Everything else is thrown away. 

#### Example Usage

You can type `!help` to get a list of current commands Q knows. 

>Michael Henry: !help 
>Q APP: I know how to do: !chuck, !food, !motivation, !nasa, !reverse, !shrug, !weather 


### Support or Contact

*Having trouble with Q?* 
Please first check if there is an existing issueon [GitHub](https://github.com/LEXmono/q/issues). If there is not then please submit a new issue.

*Have a Feature Request?*
Please first check if there is an existing issueon [GitHub](https://github.com/LEXmono/q/issues). If there is not then please [submit a new request](https://github.com/LEXmono/q/issues/new).
