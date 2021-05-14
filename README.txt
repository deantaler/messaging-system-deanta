***** messaging system *****
A REST API written in Flask, Python.
DB - ClearDB(Mysql)
Server - Heroku

How to use?
1. first thing you have to do is to create a user
2. login with user details
3. use the token from the login response to use the system functions.

Requests
1. messaging-system-dean.herokuapp.com/ - GET : greeting
2. messaging-system-dean.herokuapp.com/user - POST: create a new user {name, password}
3. messaging-system-dean.herokuapp.com/login - write your name and password in the authorization field (Postmam - Basic Auth)

*Note: copy the token from the login response and save it in 'Headers' as a value with key 'x-access-token' for all the further requests*

4. messaging-system-dean.herokuapp.com/user - GET: get all users.
5. messaging-system-dean.herokuapp.com/user/<user_id> - GET: get one user.
6. messaging-system-dean.herokuapp.com/message -POST: write message {receiver, subject, text}
7. messaging-system-dean.herokuapp.com/read_messages/<bool> - GET: read messages. True - all messages. False - only unread messages.
8. messaging-system-dean.herokuapp.com/message/<message_id> - GET: read message.
9. messaging-system-dean.herokuapp.com/message/<message_id> - DELETE: delete message.