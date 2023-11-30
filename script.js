document.addEventListener("DOMContentLoaded", function () {
    var userDropdown = document.getElementById("userDropdown");
    var loginRegisterLink = document.getElementById("loginRegisterLink");
    userDropdown.style.display = "none"

    var userLoggedIn = false; 
    function updateUserUI(){
        if (userLoggedIn) {
            userDropdown.style.display = "flex";
            loginRegisterLink.style.display = "none";
        } else {
            userDropdown.style.display = "none";
            loginRegisterLink.style.display = "block";
        }
    }

    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
        userLoggedIn = true;
    }

    // Call the function to update UI
    updateUserUI();

document.getElementById('loginButton').addEventListener('click', async (event) => {
    event.preventDefault(); 
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/auth/login?email=${email}&password=${password}`, {
            method: 'POST',
        });
        if (response.ok) {
            const { user_id, access_token } = await response.json();
            if (access_token){
                userLoggedIn = true
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('user_id', user_id);
                console.log('Logged in successfully:', {
                    "user_id":user_id, "access_token":access_token
                });
                updateUserUI()
                window.location.href = 'index.html';
                console.log(userLoggedIn)
            }else{
                console.error('Login failed');
            }
        } else {
            console.error('Login failed');
        }
    } catch (error) {
        console.error('Error during login:', error);
    }
});
});



document.addEventListener("DOMContentLoaded", function () {


// Fetch incomplete tasks
fetch('http://127.0.0.1:8000/api/v1/todos/client/1/list_incomplete_todos')
    .then(response => response.json())
    .then(data => {
        const incompleteTasksList = document.getElementById('incompleteTasksList');
        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
                <span class="" id="text-${item.id}">${item.text}</span>
                <div class="d-flex justify-content-between ">
                        <button type="submit" class="btn btn-sm  btn-success mark-completed-btn"  data-item-id="${item.id}">Mark Completed</button>


                        <button type="button" class="btn btn-sm me-2 ms-2 btn-warning edit-toggle-button" data-bs-toggle="modal" data-bs-target="#editTaskModal-${item.id}"  data-item-id="${item.id}">Edit</button>
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

                        <button type="submit" class="btn btn-sm delete-btn btn-danger"  data-item-id="${item.id}">Delete</button>
                </div>
            `;
            incompleteTasksList.appendChild(listItem);
        });

         // Add event listeners for Mark Incomplete and Delete buttons
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

    })
    .catch(error => console.error('Error fetching incomplete tasks:', error));


// Fetch completed tasks
fetch('http://127.0.0.1:8000/api/v1/todos/client/1/list_client_completed_todos')
    .then(response => response.json())
    .then(data => {
        const completedTasksList = document.getElementById('completedTasksList');
        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item bg-dark text-light d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
            <span class="">${item.text}</span>
            <div class="d-flex justify-content-between ">
                <button class="btn btn-sm btn-primary mark-incomplete-btn" data-item-id="${item.id}">Mark Incomplete</button>
                <button class="btn btn-sm btn-danger delete-btn ms-2" data-item-id="${item.id}">Delete</button>
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
        
    })
    .catch(error => console.error('Error fetching completed tasks:', error));






// Function to handle Mark Completed button click
function markCompletedHandler(event) {
    const itemId = event.target.dataset.itemId;
    // Call the endpoint to mark the task as incomplete
    fetch(`http://127.0.0.1:8000/api/v1/todos/todo/${itemId}/mark_completed`, {
        method: 'PUT',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        // Optionally, you can update the UI or handle the response
        location.reload();
    })
    .catch(error => console.error('Error marking task completed:', error));
}


// Function to handle Mark Incomplete button click
function markIncompleteHandler(event) {
    const itemId = event.target.dataset.itemId;
    // Call the endpoint to mark the task as incomplete
    fetch(`http://127.0.0.1:8000/api/v1/todos/todo/${itemId}/mark_incomplete`, {
        method: 'PUT',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        // Optionally, you can update the UI or handle the response
        location.reload();
    })
    .catch(error => console.error('Error marking task incomplete:', error));
}

// Function to handle Delete button click
function deleteHandler(event) {
    const itemId = event.target.dataset.itemId;
    // Call the endpoint to delete the task
    fetch(`http://127.0.0.1:8000/api/v1/todos/todo/${itemId}/delete`, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        // Optionally, you can update the UI or handle the response
        location.reload();

    })
    .catch(error => console.error('Error deleting task:', error));
}

    const addTodoForm = document.getElementById('addTodoForm');
    const todoContentInput = document.getElementById('todoContent');
    const submitTodoButton = document.getElementById('submitTodo');

    submitTodoButton.addEventListener('click', function () {
        const todoContent = todoContentInput.value;

        // Check if the todo content is not empty
        if (todoContent !== '') {
            // Call the endpoint to create a todo object
            fetch(`http://127.0.0.1:8000/api/v1/todos/client/1/todo/create/${todoContent}`, {
                method: 'POST',
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                // Optionally, you can handle the response or update the UI
                console.log('Todo created successfully!');
                location.reload();
                // Clear the input field after successful submission
                todoContentInput.value = '';
            })
            .catch(error => console.error('Error creating todo:', error));
        } else {
            // Handle empty todo content (optional)
            console.log('Todo content cannot be empty.');
        }
    });


    function editHandler(event) {

        const itemId = event.target.getAttribute('data-item-id');
        const todoFormEdit = document.getElementById(`todoFormEdit-${itemId}`);
        const todoContentInputEdit = document.getElementById(`todoContentEdit-${itemId}`);
        const submitTodoButtonEdit = document.getElementById(`submitTodoEdit-${itemId}`);
        
        submitTodoButtonEdit.addEventListener('click', function () {
            const todoContentEdit = todoContentInputEdit.value;
            
            // Check if the todo content is not empty
            if (todoContentEdit !== '') {
                // Call the endpoint to create a todo object
                fetch(`http://127.0.0.1:8000/api/v1/todos/todo/${itemId}/update/${todoContentEdit}`, {
                    method: 'PUT',
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                // Optionally, you can handle the response or update the UI
                console.log('Todo edited successfully!');
                location.reload();
                // Clear the input field after successful submission
                todoContentInputEdit.value = '';
            })
            .catch(error => console.error('Error edit todo:', error));
        } else {
            // Handle empty todo content (optional)
            console.log('Todo content cannot be empty.');
        }
        
    });
}
// const storedToken = localStorage.getItem('access_token')
// const storedId = localStorage.getItem('user_id')






});





// https://www.16personalities.com/profiles/3aa7a1ecc1814






