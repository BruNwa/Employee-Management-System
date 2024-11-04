
function loadContent(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('content-area').innerHTML = data;
        })
        .catch(error => {
            document.getElementById('content-area').innerHTML = "<p>Failed to load content. Please try again.</p>";
            console.error("Error loading content:", error);
        });
}
function submitEmployeeForm() {
    const form = document.querySelector("form"); // Select the form element
    const formData = new FormData(form); // Gather form data
    const url = form.action; // Get the action URL from the form

    fetch(url, {
        method: form.method, // Use POST or GET based on the form method
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'An error occurred'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Employee created successfully!'); // Show success message
                // Optionally, clear the form fields if needed
                form.reset(); // Resets the form fields if you want to keep adding more employees
            }
        })
        .catch(error => {
            alert('Error: ' + error.message); // Show error message
        });
}

function submitForm(button) {
    const row = button.closest('tr');
    const roleId = row.querySelector('input[name="role_id"]').value;
    const baseSalary = row.querySelector('input[name="base_salary"]').value;
    const salaryType = row.querySelector('select[name="salary_type"]').value;

    const formData = new FormData();
    formData.append('role_id', roleId);
    formData.append('base_salary', baseSalary);
    formData.append('salary_type', salaryType);

    fetch('/salary-setup', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text); });
            }
            return response.json();
        })
        .then(data => {
            alert(data.message); // Show success message
            loadContent('/salary-setup'); // Reload the content to see updated roles
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            alert("There was an error updating the role salary data.");
        });
}

// Attach an event listener to the dynamically loaded content area for form submission
document.getElementById('content-area').addEventListener('submit', function (event) {
    if (event.target.tagName === 'FORM') {
        event.preventDefault();
        submitForm(event.target);
    }
});
function deleteEmployee(employeeId, button) {
    const url = `/crud/employee/delete/${employeeId}`; // Construct the delete URL

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || 'An error occurred'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(data.message); // Show success message
                const row = button.closest('tr'); // Get the row to delete
                row.remove(); // Remove the row from the table
            }
        })
        .catch(error => {
            alert('Error: ' + error.message); // Show error message
        });
}

function updateStatus(paymentId, newStatus) {
    fetch(`/payslip/payments/update_status/${paymentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(`Payment status updated to ${newStatus}`);
                location.reload();  // Reload to reflect changes
            } else {
                alert('Error updating payment status: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error updating the payment status.');
        });
}

function runPaymentTest(paymentId) {
    fetch(`/payslip/payments/run_test/${paymentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(data.message);  // Show the success message returned by the server
                location.reload();  // Reload to reflect changes
            } else {
                alert('Error running payment test: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error running the payment test.');
        });
}

function handleLeaveAction(url, action) {
    const confirmation = action === 'approve' ? 'approve this leave request?' : 'reject this leave request?';
    if (confirm(`Are you sure you want to ${confirmation}`)) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);  // Show the message returned by the server
                location.reload();  // Reload the page to reflect changes
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error processing your request.');
            });
    }
}

function filterAttendance() {
    // Get form input values
    const employeeId = document.getElementById('employee_id').value;
    const date = document.getElementById('date').value;

    // Create query string parameters
    const params = new URLSearchParams({ employee_id: employeeId, date: date });

    // Fetch filtered attendance data
    fetch(`/attendance/?${params.toString()}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // Identifies it as an AJAX request
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            // Update the attendance table body with the response data
            document.querySelector('#attendanceTable tbody').innerHTML = data;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your request.');
        });
}


// Function to handle filtering performance records
function filterPerformanceRecords() {
    const employeeId = document.getElementById('employee_id').value;
    const reviewerId = document.getElementById('reviewer_id').value;

    const params = new URLSearchParams({
        employee_id: employeeId,
        reviewer_id: reviewerId
    });

    fetch(`/performance/?${params.toString()}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Identifies it as an AJAX request
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text(); // Get the response text
        })
        .then(data => {
            console.log("Fetched Data:", data); // Log the data
            document.querySelector('tbody').innerHTML = data; // Update the table body with new rows
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your request.');
        });
}

function generatePayslip() {
    // Prevent the form's default submission
    event.preventDefault();

    // Create a FormData object from the form
    const formData = new FormData(document.getElementById('generatePayslipForm'));
    const params = new URLSearchParams(formData).toString();

    // Fetch request to send form data and update the page with the response
    fetch(`/payslip/generate`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: params
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            // Update the page with the payslip results
            document.getElementById('payslipResult').innerHTML = data;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your request.');
        });
}

function logout() {
    fetch('/login/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Logout successful') {
                window.location.href = '/login';
            } else {
                throw new Error('Logout failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Logout failed. Please try again.');
        });
}
