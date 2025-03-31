document.addEventListener("DOMContentLoaded", function () {
    // const userDropdown = document.getElementById("userDropdown");
    // const clientUsername = document.getElementById("clientUsername");
    // const userImage = document.getElementById("userImage");
    // const logoutButton = document.getElementById("logout");
    const todoContentInput = document.getElementById("todoContent");
    // const addTodoForm = document.getElementById('addTodoForm');
    const submitTodoButton = document.getElementById("submitTodo");
    
    const incompleteTasksList = document.getElementById("incompleteTasksList");
    const completedTasksList = document.getElementById("completedTasksList");
    // const storedUsername = localStorage.getItem("username");
    // const storedImage = localStorage.getItem("image");
    const storedAccessToken = localStorage.getItem("access_token");
    // const storedRefreshToken = localStorage.getItem("refresh_token");
    const storedId = localStorage.getItem("id");
    // const defaultUserImage = "https://icons.veryicon.com/png/o/miscellaneous/indata/user-circle-1.png";
    // let userLoggedIn = false;


    const BASE_URL = "http://127.0.0.1:8000/api/v1"
;

    

    function getAuthHeaders() {
        const token = localStorage.getItem("access_token");
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    

    function start(){
        fetchIncompleteTasks();
        fetchCompletedTasks();
    }


    document.getElementById("addTodoForm").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent form submission if needed
            document.getElementById("submitTodo").click(); // Trigger the button click
        }
    });
    


    // Fetch incomplete tasks
    async function fetchIncompleteTasks() {
        try {
            const response = await fetchWithAuth(`${BASE_URL}/todos/client/${storedId}/list_incomplete_todos`, {
                method: 'GET',
                headers: {
                    
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const incompleteTasks = await response.json();
            incompleteTasks.forEach(item => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    <span class="" id="text-${item.id}">${item.text}</span>
                    <div class="d-flex items-center justify-content-between ">
                            <button type="submit" class="btn btn-sm  btn-success mark-completed-btn fixed-btn"  data-item-id="${item.id}">Mark Completed</button>


                            <button type="button" class="btn btn-sm me-2 ms-2 btn-warning edit-toggle-button fixed-btn" data-bs-toggle="modal" data-bs-target="#editTaskModal-${item.id}"  data-item-id="${item.id}">Edit</button>
                            <!-- Modal -->
                            <div class="modal fade" id="editTaskModal-${item.id}" tabindex="-1" aria-labelledby="editTaskModalLabel" aria-hidden="true">
                            <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                                <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title text-dark" id="editTaskModalLabel">Edit Task</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body text-dark">
                                    <form id="todoFormEdit-${item.id}" class="form-inline">
                                        <input type="text" id="todoContentEdit-${item.id}" class="form-control mb-2 mr-sm-2" placeholder="Type here...">
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Close</button>
                                    <button type="button" class="btn btn-sm btn-primary animate__animated animate__swing edit-btn"  id="submitTodoEdit-${item.id}" data-item-id="${item.id}">Save changes</button>
                                </div>
                                </div>
                            </div>
                            </div>

                            <button type="submit" class="btn btn-sm delete-btn btn-danger fixed-btn"  data-item-id="${item.id}">Delete</button>
                    </div>
                `;
                incompleteTasksList.appendChild(listItem);
            });
            
            document.querySelectorAll('.mark-completed-btn').forEach(button => {
                button.addEventListener('click', markCompletedHandler);
            });

            document.querySelectorAll('.edit-btn').forEach(button => {
                button.addEventListener('click', editHandler);
            });

            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', deleteHandler);
            });

            document.querySelectorAll('.edit-toggle-button').forEach(button => {
                button.addEventListener('click', preEditHandler);
            });

            function preEditHandler(event){
                const itemId = event.target.getAttribute('data-item-id');
                const taskText = document.getElementById(`text-${itemId}`); // Implement a function to get the task text by ID
                const todoContentInputEdit = document.getElementById(`todoContentEdit-${itemId}`);
                const textttt = taskText.innerHTML
                todoContentInputEdit.value = textttt;
            }


        } catch (error) {
            console.error('Error Fetching Incomplete Todos:', error);
        }
    };

    async function fetchCompletedTasks() {
        try {
            const response = await fetchWithAuth(`${BASE_URL}/todos/client/${storedId}/list_client_completed_todos`, {
                method: 'GET',
                headers: {
                    
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const completedTasks = await response.json();
            completedTasks.forEach(item => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item bg-dark text-light d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                <span class="">${item.text}</span>
                <div class="d-flex justify-content-between ">
                    <button class="btn btn-sm btn-primary mark-incomplete-btn fixed-btn" data-item-id="${item.id}">Mark Incomplete</button>
                    <button class="btn btn-sm btn-danger delete-btn ms-2 fixed-btn" data-item-id="${item.id}">Delete</button>
                </div>
                `;
                completedTasksList.appendChild(listItem);
            });
            
            // Add event listeners for Mark Incomplete and Delete buttons
            document.querySelectorAll('.mark-incomplete-btn').forEach(button => {
                button.addEventListener('click', markIncompleteHandler);
            });

            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', deleteHandler);
            });

        } catch (error) {
            console.error('Error Fetching Incomplete Todos:', error);
        }
    };





    // Function to handle Mark Completed button click
    async function markCompletedHandler(event) {
        const itemId = event.target.dataset.itemId;
        // Call the endpoint to mark the task as incomplete
        try{
            const response = await fetchWithAuth(`${BASE_URL}/todos/todo/${itemId}/mark_completed`, {
                method: 'PUT',
                headers: {
                    
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
        }catch (error) {
            console.error('Error marking task completed:', error);
        }
        
    }


    // Function to handle Mark Incomplete button click
    async function markIncompleteHandler(event) {
        const itemId = event.target.dataset.itemId;
        // Call the endpoint to mark the task as incomplete
        try{
            const response = await fetchWithAuth(`${BASE_URL}/todos/todo/${itemId}/mark_incomplete`, {
                method: 'PUT',
                headers: {
                    
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
        }catch{(error => console.error('Error marking task completed:', error))};
    }

    // Function to handle Delete button click
    async function deleteHandler(event) {
        const itemId = event.target.dataset.itemId;
        // Call the endpoint to delete the task
        try{
            const response = await fetchWithAuth(`${BASE_URL}/todos/todo/${itemId}/delete`, {
                method: 'DELETE',
                headers: {
                    // 
                    'Content-Type': 'application/json'
                }
                // windows.location.reload();
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
        }catch (error) {
            console.error('Error deleting task:', error);
        }
    }
    
    

    submitTodoButton.addEventListener('click', async function (event) {
        event.preventDefault();
        const todoContent = todoContentInput.value;
        // Check if the todo content is not empty
        if (todoContent !== '') {
            let formData = new FormData();
            formData.append("text", todoContent);
            // Call the endpoint to create a todo object
            try{
                const response = await fetchWithAuth(`${BASE_URL}/todos/client/${storedId}/todo/create`, {
                    body: formData,
                    method: 'POST',
                    headers: {
                        
                    }
                });
                todoContentInput.value = '';
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
            }catch{(error => console.error('Error Creating task:', error))};
                // Optionally, you can handle the response or update the UI
        } else {
            // Handle empty todo content (optional)
            console.warn('Todo content cannot be empty.');
            showAlert("Todo content cannot be empty.", "warning");

        }
    });


    function editHandler(event) {
        const itemId = event.target.getAttribute('data-item-id');
        const todoContentInputEdit = document.getElementById(`todoContentEdit-${itemId}`);
        const submitTodoButtonEdit = document.getElementById(`submitTodoEdit-${itemId}`);
    
        submitTodoButtonEdit.addEventListener('click', async function () {
            const todoContentEdit = todoContentInputEdit.value.trim();
    
            if (todoContentEdit !== '') {
                try {
                    const response = await fetchWithAuth(`${BASE_URL}/todos/todo/${itemId}/update`, {
                        method: 'PUT',
                        body: JSON.stringify({ text: todoContentEdit }),  
                        headers: {
                            
                            'Content-Type': 'application/json'  
                        }
                    });
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                } 
                catch (error) {console.error('Error Editing Task:', error);}
            } 
            
            else {console.warn('Todo content cannot be empty.'); showAlert("Todo content cannot be empty.", "warning");}
        });
    }
    
    function showAlert(message, type) {
        alertContainer.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        setTimeout(() => alertContainer.innerHTML = "", 3000);
    }

    async function getUserImage() {
        try {
            const response = await fetchWithAuth(`${BASE_URL}/auth2/get_user_image`, {
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
                console.log(result.errors?.error || "Error fetching image", "danger");
                return null;
            }
        } catch (error) {
            console.log("Something went wrong. Try again.", "danger");
            return null;
        }
    }


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

    start();
});










