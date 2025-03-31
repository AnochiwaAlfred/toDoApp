document.addEventListener("DOMContentLoaded", function () {
    const userImage = document.getElementById("userImage");
    const storedUsername = localStorage.getItem("username");
    const storedImage = localStorage.getItem("image");
    const storedRefreshToken = localStorage.getItem("refresh_token");
    const storedId = localStorage.getItem("id");
    const storedAccessToken = localStorage.getItem("access_token");
    const defaultUserImage = "https://icons.veryicon.com/png/o/miscellaneous/indata/user-circle-1.png";
    const BASE_URL = "http://127.0.0.1:8000/api/v1"



    let userLoggedIn = false;


    function toTitleCase(str) {
        return str.replace(/\w\S*/g, function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    }

    if (storedAccessToken) {
        userLoggedIn = true;
    }

    async function updateImage(){
        
        userImage.src = storedImage || defaultUserImage;
        let image = await getUserImage()
        if(image){
            localStorage.setItem("image", image);
            userImage.src = image;
        }
    }

    async function updateUserUI(){
        
        if (!userLoggedIn) {
            window.location.href = "login.html";
        } 
        clientUsername.innerHTML = toTitleCase(storedUsername || "User");
        userImage.src = storedImage || defaultUserImage;
        let image = await getUserImage()
        if(image){
            userImage.src = image;
        }
    }
   

    async function getUserImage() {
        try {
            const response = await fetchWithAuth(`${BASE_URL}/auth2/get_user_image`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                },

            });
    
            const result = await response.json();
    
            if (response.ok && result.image) {
                return result.image;
            } else {
                console.log(result.errors?.error || "Error fetching image", "danger");
                return null;
            }
        } catch (error) {
            console.log("Something went wrong. Try again.", "danger");
            return null;
        }
    }
    
    function showAlert(message, type) {
        alertContainer.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        setTimeout(() => alertContainer.innerHTML = "", 3000);
    }

    // Handle Logout
    document.getElementById('logout').addEventListener('click', async (event) => {
        event.preventDefault();
        if (!storedAccessToken) {
            console.error('No access token found.');
            return;
        }
        try {
            const response = await fetchWithAuth(`${BASE_URL}/auth2/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${storedAccessToken}`,
                }
            });
    
            if (response.ok) {
                localStorage.clear();
                userLoggedIn = false;
                // updateUserUI();
            } else {
                console.warn('Logout failed:', response.statusText);
                showAlert("Logout failed.", "warning");
                
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    });

    async function fetchWithAuth(url, options = {}) {
        let response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            },
        });
    
        if (response.status === 401) {
            // Access token expired, try refreshing
            const refreshResponse = await fetch(`${BASE_URL}/refresh_token`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: localStorage.getItem("refresh_token") }),
            });
    
            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                localStorage.setItem("access_token", data.access_token);
                return fetchWithAuth(url, options); // Retry original request
            } else {
                localStorage.clear();
                window.location.href = "login.html"; // Redirect to login
            }
        }
    
        return response;
    }
    
    updateImage();
    updateUserUI();

  });
