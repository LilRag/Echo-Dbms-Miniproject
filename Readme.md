# Echo 
“Echo" is a social media blogging platform that enables users to create and manage their posts. It fosters interaction by allowing users to follow others, comment on posts, and express appreciation through likes. The platform also helps users discover new content via a personalized feed, trending topics, and updates from their friends.



Tech Stack 
Frontend : React 
Backend : Django
Database : MySQL
API: Django REST Framework (DRF)

Your React application runs in the user's browser, providing the interactive user experience.

When a user performs an action (like making a post or liking something), the React app sends a request to your Django REST Framework API.

The Django backend receives this request, processes the logic (e.g., "save this new post"), and interacts with the MySQL database to store or retrieve data.

Django then sends a response back to your React app, which updates the UI to show the new post or the updated like count without needing to reload the entire page.
