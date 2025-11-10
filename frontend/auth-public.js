// auth-public.js
const CURRENT_USER_ID = localStorage.getItem('current_user_id');

// If a user ID IS found, they are already logged in.
// Send them to the main app (index.html).
if (CURRENT_USER_ID) {
    window.location.href = 'index.html';
}