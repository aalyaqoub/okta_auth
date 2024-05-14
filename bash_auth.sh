#!/bin/bash
# An example of how to get an access token from a login page. You will need to add http://localhost:54672 to 
# the redirect urls in the OAuth2 application settings and modify the redirect url in the fastapi script.


# open the login page this is assuming you are using the fastapi script
xdg-open "http://localhost:3000/login" &

# create endpoint and get access token
port=54672
access_token=$(echo -e "HTTP/1.1 200 OK\n\n" | nc -l -p $port -q 1 | grep -oP 'access_token=\K[^&]*')

# Print the access token
echo "Access Token: $access_token"

# exit the script
exit 0