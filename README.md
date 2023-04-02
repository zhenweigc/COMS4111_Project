# COMS4111_Project
A project for COMS4111 database

# What we implemented
In the initial proposal, we planned to have search functions for game, which includes search by name and genre.
Furthermore, users can like and dislike games, where disliked games will not appear in the search result unless removed by users.

We implemented all functions that we proposed. Note that in order to like/dislike a game, users must login.
Furthermore, users can undo like/dislike on a game, and delete their account.
For our main page, we put some texts to introduce the background and context of the search engine. On the upper right corner of all webpages, their are five options: 'home', 'profile', 'login', 'register' and 'logout'.
'home' will redirect the user to the main index. There are two search boxes in the index, where users can search for their interested games using the first one.
Users can not only enter the name of the game, but also the genre that the game belongs to.
Based on the user’s input, the database will retrieve relevant information and form a table on the webpage.
Once the user finds the game and its game id, he/she can put this into the second search box to find out its reviews.
Users can like/dislike games displayed in the search result. Of course, they will have to login first. They can obtain their accounts by clicking 'register'. Note that the website requires a minimum password length of 6, and duplicated username is not allowed.
Disliked games will not show up in further searches.
Another interesting page is the profile page. This page also requires login. On this page, users can view lists of games that they liked/disliked and modify lists.
Users can also delete their accounts by clicking the 'delete account' button. Of course, user needs to be logged in and enter their password to confirm such action.
Finally, users can logout and clear their session by clicking 'logout'.
