document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.querySelector("form");
    const registerButton = document.getElementById("registerButton");
    const BASE_URL = "http://127.0.0.1:8000/api/v1"


    registerButton.addEventListener("click", async function(event) {
        event.preventDefault();
    
        let email = document.getElementById("registerEmailInput").value;
        let username = document.getElementById("registerUsernameInput").value;
        let phone = document.getElementById("registerPhoneInput").value;
        let password = document.getElementById("registerPasswordInput").value;
        let passwordConfirm = document.getElementById("registerConfirmPasswordInput").value;
    
        let formData = new FormData();
        formData.append("email", email);
        formData.append("username", username);
        formData.append("phone", phone);
        formData.append("password", password);
        formData.append("passwordConfirm", passwordConfirm);

        // Clear previous error messages
        const alertContainer = document.getElementById("alertContainer");
        alertContainer.innerHTML = "";
    
        try {
            let response = await fetch(`${BASE_URL}/auth2/register`, {
                method: "POST",
                body: formData
            });
    
            let result = await response.json();
    
            if (response.ok) {
                alert("Registration successful! Redirecting to login...");
                window.location.href = "login.html";
            } else {
                displayErrors(result);
            }
        } catch (error) {
            console.error("Error:", error);
            displayErrors({ error: "An error occurred. Please try again." });
        }
    });

    function displayErrors(errors) {
        console.log(errors);
        const alertContainer = document.getElementById("alertContainer");
        
        let errorHtml = `
            <div class="alert alert-danger animate__animated animate__fadeIn alert-dismissible fade show" role="alert">
                <strong>Registration Failed!</strong>
                <ul class="mt-2">
        `;

        if (typeof errors === "string") {
            errorHtml += `<li>${errors}</li>`;
        } else if (errors.error) {
            errorHtml += `<li>${errors.error}</li>`;
        } else {
            for (const [key, value] of Object.entries(errors.errors)) {
                errorHtml += `<li><strong>${value}:</strong></li>`;
            }
        }

        errorHtml += `
                </ul>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        alertContainer.innerHTML = errorHtml;

        // Smooth scroll to the error message
        alertContainer.scrollIntoView({ behavior: "smooth", block: "center" });

        // Auto-dismiss alert after 5 seconds
        setTimeout(() => {
            document.querySelector(".alert").classList.add("animate__fadeOut");
            setTimeout(() => {
                alertContainer.innerHTML = "";
            }, 1000); // Give fade-out animation some time
        }, 20000);
    }
});
