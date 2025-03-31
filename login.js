document.addEventListener("DOMContentLoaded", function () {
    const loginButton = document.getElementById("loginButton");
    const BASE_URL = "http://127.0.0.1:8000/api/v1"

    loginButton.addEventListener("click", async function(event) {
        event.preventDefault();

        let email = document.getElementById("emailInput").value;
        let password = document.getElementById("passwordInput").value;

        let formData = new FormData();
        formData.append("username_or_email", email);
        formData.append("password", password);

        // Clear previous alerts
        const alertContainer = document.getElementById("alertContainer");
        alertContainer.innerHTML = "";

        try {
            let response = await fetch(`${BASE_URL}/auth2/login`, {
                method: "POST",
                body: formData
            });

            let result = await response.json();

            if (response.ok) {
                localStorage.setItem("access_token", result.access_token);
                localStorage.setItem("refresh_token", result.refresh_token);
                localStorage.setItem("username", result.username);
                localStorage.setItem("id", result.id);
                
                let image = await getUserImage()

                if(image){
                    localStorage.setItem("image", image);
                }
                displaySuccess("Login successful! Redirecting...");
                setTimeout(() => window.location.href = "index.html", 2000);
            } else {
                displayErrors(result);
            }
        } catch (error) {
            console.error("Error:", error);
            displayErrors({ error: "An error occurred. Please try again." });
        }
    });

    function displayErrors(errors) {
        const alertContainer = document.getElementById("alertContainer");
        let errorHtml = `
            <div class="alert alert-danger animate__animated animate__fadeIn" role="alert">
                <strong>Login Failed!</strong>
                <ul class="mt-2">
        `;

        if (typeof errors === "string") {
            errorHtml += `<li>${errors}</li>`;
        } else if (errors.error) {
            errorHtml += `<li>${errors.error}</li>`;
        } else {
            for (const [key, value] of Object.entries(errors.errors)) {
                errorHtml += `<li><strong>${key}:</strong> ${value}</li>`;
            }
        }

        errorHtml += "</ul></div>";
        alertContainer.innerHTML = errorHtml;
    }

    function displaySuccess(message) {
        const alertContainer = document.getElementById("alertContainer");
        alertContainer.innerHTML = `
            <div class="alert alert-success animate__animated animate__fadeIn" role="alert">
                <strong>${message}</strong>
            </div>
        `;
    }

    async function getUserImage() {
        const storedAccessToken = localStorage.getItem("access_token"); // Retrieve the token
        if (!storedAccessToken) return null; // Ensure token exists
    
        try {
            const response = await fetch(`${BASE_URL}/auth2/get_user_image`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${storedAccessToken}`,
                    "Content-Type": "application/json"
                },
            });
    
            const result = await response.json();
    
            if (response.ok && result.image) {
                return result.image;
            } else {
                return null;
            }
        } catch (error) {
            console.error("Error fetching user image:", error);
            return null;
        }
    }
     
});
