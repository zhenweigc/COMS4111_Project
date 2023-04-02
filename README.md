# COMS4111_Project
A project for COMS4111 database

# What we implemented
In the initial proposal, we planned to have search functions for game, which includes search by name and genre.
Furthermore, users can like and dislike games, where disliked games will not appear in the search result unless removed by users.

We implemented all functions that we proposed. Note that in order to like/dislike a game, users must login.
Furthermore, users can undo like/dislike on a game, and delete their account.
For our main page, we put some texts to introduce the background and context of the search engine. On the upper right corner of all webpages, their are five options: 'home', 'profile', 'login', 'register' and 'logout'.

'home' will redirect the user to the main index, which is the first interesting webpage in our project. There are two search boxes in the index, where users can search for their interested games using the first one.
Users can not only enter the name of the game, but also the genre that the game belongs to.
Based on the user’s input, the database will genereate a SQL query which retrieves relevant information from games and game_genre. Results will form a table and displayed on the webpage after filtering.
Once the user finds the game and its game id, he/she can put this into the second search box to find out its reviews. The python program will again generate a simple query and get reviews from the 'review' table.

Users can like/dislike games displayed in the search result. Of course, they will have to login first. They can obtain their accounts by clicking 'register'. Note that the website requires a minimum password length of 6, and duplicated username is not allowed. When clicking like/dislike buttom, a POST request will be triggered, and such game will be inserted into the corresponding 'user_(dis)liked_game' table. Disliked games will not show up in further searches, as the front-end webpage will filter it out. 

The second interesting page is the profile page. This page also requires login. On this page, users can view lists of games that they liked/disliked and modify lists. Again, this will interact with the database which will delete corresponding entry with respect to what the user clicked.
Users can also delete their accounts by clicking the 'delete account' button. Of course, user needs to be logged in and enter their password to confirm such action. After that, his/her account along with liked/disliked data will be removed from database.

Finally, users can logout and clear their session by clicking 'logout'.


# Database URLs:
We used the first database, which has an ip address of 34.148.107.47

The DB account is still 'fl2627'.

The external IP for the VM instance is 
