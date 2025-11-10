// This file controls the main "shell" of your application.

// --- 1. Get Auth State ---
const LOGGED_IN_USER_ID = sessionStorage.getItem('current_user_id');
const path = window.location.pathname.split('/').pop();

// --- 2. Auth Guard ---
// Pages that require you to be logged IN
const privatePages = [
    'index.html', 
    'profile.html', 
    'create-post.html', 
    'notifications.html',
    '' // Handles the root folder
];
// Pages that require you to be logged OUT
const publicPages = ['login.html', 'signup.html'];

// --- 3. Run Auth Checks ---
if (privatePages.includes(path) && !LOGGED_IN_USER_ID) {
    // User is not logged in but on a private page, send to login.
    window.location.href = 'login.html';
} else if (publicPages.includes(path) && LOGGED_IN_USER_ID) {
    // User is logged in but on a public page, send to home.
    window.location.href = 'index.html';
}

// NOTE: 'explore.html' is not in either list. It's a public page
// that can be viewed by anyone, logged in or out.

// --- 4. Sidebar/UI Logic ---
document.addEventListener('DOMContentLoaded', () => {
    
    // Find the placeholder on the current page
    const placeholder = document.getElementById('sidebar-placeholder');
    if (!placeholder) {
        // This page (like login/signup) doesn't have a sidebar, so do nothing.
        return;
    }

    // This is the key: We build a sidebar based on login state.
    if (LOGGED_IN_USER_ID) {
        // --- BUILD LOGGED-IN SIDEBAR ---
        buildLoggedInSidebar(placeholder);
        
        // Add event listener for the logout button
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                sessionStorage.removeItem('current_user_id');
                sessionStorage.removeItem('current_username');
                window.location.href = 'login.html';
            });
        }
        
        // Fetch notification count
        fetchUnreadCount();

    } else {
        // --- BUILD LOGGED-OUT SIDEBAR ---
        buildLoggedOutSidebar(placeholder);
    }
});


// --- 5. Sidebar HTML Builder Functions ---

function buildLoggedInSidebar(placeholder) {
    // Find the active page
    const activePage = (path === '' || path === 'index.html') ? 'home' : 
                       (path === 'explore.html') ? 'explore' :
                       (path === 'notifications.html') ? 'notifications' :
                       (path.startsWith('profile.html')) ? 'profile' : 'other';

    const sidebarHTML = `
        <aside class="w-64 flex-shrink-0 bg-white border-r border-gray-200 hidden md:block">
            <div class="p-6">
                <h1 class="text-3xl font-extrabold text-gray-800">
                    <a href="index.html"><span class="text-emerald-500">Echo</span></a>
                </h1>
            </div>
            <nav class="mt-6 px-4">
                <a href="index.html" class="sidebar-link ${activePage === 'home' ? 'active' : ''} flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg">
                    <i class="fas fa-home w-6 text-center"></i>
                    <span class="ml-4">Home</span>
                </a>
                <a href="explore.html" class="sidebar-link ${activePage === 'explore' ? 'active' : ''} flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <i class="fas fa-compass w-6 text-center"></i>
                    <span class="ml-4">Explore</span>
                </a>
                <a href="notifications.html" id="sidebar-notifications-link" class="sidebar-link ${activePage === 'notifications' ? 'active' : ''} flex items-center justify-between px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <div class="flex items-center">
                        <i class="fas fa-bell w-6 text-center"></i>
                        <span class="ml-4">Notifications</span>
                    </div>
                    <span id="notification-badge" class="hidden w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"></span>
                </a>
                <a href="profile.html?user_id=${LOGGED_IN_USER_ID}" id="sidebar-profile-link" class="sidebar-link ${activePage === 'profile' ? 'active' : ''} flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <i class="fas fa-user w-6 text-center"></i>
                    <span class="ml-4">Profile</span>
                </a>
                
                <div class="border-t my-4"></div>
                <a href="#" id="logout-button" class="sidebar-link flex items-center px-4 py-3 text-red-500 hover:bg-red-50 rounded-lg mt-2">
                    <i class="fas fa-sign-out-alt w-6 text-center"></i>
                    <span class="ml-4">Logout</span>
                </a>
            </nav>
            <div class="px-6 mt-8">
                <a href="create-post.html" class="block w-full text-center bg-emerald-500 text-white font-semibold px-5 py-3 rounded-lg hover:bg-emerald-600 transition-colors">
                    New Post
                </a>
            </div>
        </aside>
    `;
    placeholder.innerHTML = sidebarHTML;
}

function buildLoggedOutSidebar(placeholder) {
    // Find the active page
    const activePage = (path === 'explore.html') ? 'explore' : 'other';

    const sidebarHTML = `
        <aside class="w-64 flex-shrink-0 bg-white border-r border-gray-200 hidden md:block">
            <div class="p-6">
                <h1 class="text-3xl font-extrabold text-gray-800">
                    <a href="explore.html"><span class="text-emerald-500">Echo</span></a>
                </h1>
            </div>
            <nav class="mt-6 px-4">
                <a href="explore.html" class="sidebar-link ${activePage === 'explore' ? 'active' : ''} flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <i class="fas fa-compass w-6 text-center"></i>
                    <span class="ml-4">Explore</span>
                </a>
                
                <div class="border-t my-4"></div>
                <a href="login.html" class="sidebar-link flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <i class="fas fa-sign-in-alt w-6 text-center"></i>
                    <span class="ml-4">Login</span>
                </a>
                <a href="signup.html" class="sidebar-link flex items-center px-4 py-3 text-gray-500 hover:bg-gray-100 rounded-lg mt-2">
                    <i class="fas fa-user-plus w-6 text-center"></i>
                    <span class="ml-4">Sign Up</span>
                </a>
            </nav>
            <div class="px-6 mt-8">
                <a href="login.html" class="block w-full text-center bg-emerald-500 text-white font-semibold px-5 py-3 rounded-lg hover:bg-emerald-600 transition-colors">
                    New Post
                </a>
            </div>
        </aside>
    `;
    placeholder.innerHTML = sidebarHTML;
}

// --- 6. Notification Function ---
async function fetchUnreadCount() {
    const badge = document.getElementById('notification-badge');
    if (!badge || !LOGGED_IN_USER_ID) return;
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${LOGGED_IN_USER_ID}/notifications/unread-count`);
        if (!response.ok) return;
        const data = await response.json();
        if (data.unread_count > 0) {
            badge.textContent = data.unread_count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    } catch (error) {
        console.error("Failed to fetch notification count:", error);
    }
}