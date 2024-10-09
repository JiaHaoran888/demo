document.addEventListener('DOMContentLoaded', function () {
    // 登录处理
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(loginForm);
            fetch('/login', {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/welcome';
                    } else {
                        alert('Login failed! Please try again.');
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // 删除学生
    const deleteButtons = document.querySelectorAll('.delete-student');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const studentEmail = this.dataset.email;
            const confirmed = confirm('Are you sure you want to delete this student?');
            if (confirmed) {
                fetch(`/delete_student/${studentEmail}`, {
                    method: 'POST',
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            alert('Error deleting student.');
                        }
                    });
            }
        });
    });

    // 添加学生
    const addStudentForm = document.getElementById('addStudentForm');
    if (addStudentForm) {
        addStudentForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(addStudentForm);
            fetch('/add_student', {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error adding student.');
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }
});

function searchStudent(populationCode) {
    const query = document.getElementById('searchQuery').value;
    const resultsContainer = document.getElementById('searchResults');

    fetch(`/search_student?query=${query}&population_code=${populationCode}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';
            data.forEach(student => {
                const li = document.createElement('li');
                li.textContent = `${student.contact_first_name} ${student.contact_last_name} (${student.student_epita_email})`;
                resultsContainer.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
}


// Handle Delete Student button click
$(document).on('click', '.delete-student-btn', function() {
    const email = $(this).data('email');
    if (confirm('Are you sure you want to delete this student?')) {
        $.ajax({
            url: '/delete_student',
            method: 'POST',
            data: { email: email },
            success: function(response) {
                if (response.success) {
                    $(`#student-row-${email}`).remove();
                } else {
                    alert('Error deleting student: ' + response.error);
                }
            }
        });
    }
});

// Handle Edit Student button click
$(document).on('click', '.edit-student-btn', function() {
    const email = $(this).data('email');
    const firstName = $(this).data('first');
    const lastName = $(this).data('last');
    $('#editStudentEmail').val(email);
    $('#editStudentFirstName').val(firstName);
    $('#editStudentLastName').val(lastName);
    $('#editStudentModal').modal('show');
});

$(document).ready(function() {
    $('#search-course-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '/search_and_assign_course',
            method: 'POST',
            data: $(this).serialize(),
            cache: false, // Disable caching
            success: function(response) {
                console.log('Response:', response); // Log the response for debugging
                if (response.success) {
                    let resultsHtml = '';
                    response.courses.forEach(course => {
                        resultsHtml += `<tr>
                            <td>${course.course_code}</td>
                            <td>${course.course_name}</td>
                        </tr>`;
                    });
                    $('#course-search-results-body').html(resultsHtml);
                    $('#courseSearchResults').show();
                } else {
                    alert('Error searching course: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error: ' + status + ' ' + error);
            }
        });
    });
});
