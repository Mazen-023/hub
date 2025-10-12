document.addEventListener('DOMContentLoaded', function () {
    
    // Delete specific project
    document.querySelectorAll('.delete-btn').forEach(button => { delete_project(button) });

    // Botton to toggle follow
    const followBtn = document.querySelector('#toggle_follow');
    if (followBtn) {
        followBtn.addEventListener('click', function () {
            const userId = this.dataset.user;
            toggle_follow(userId);
        });
    }

    // Star Feature
    document.querySelectorAll('.star-btn').forEach(button => { star(button) });

    // Review Feature
    const reviewBtn = document.querySelector('#review-btn');
    if (reviewBtn) {
        reviewBtn.addEventListener('click', review);
    }

    // Image Upload
    const photoForm = document.querySelector('#photo-form');
    if (photoForm) {
        photoForm.addEventListener('change', upload_photo);
    }
    
    // Project visibility
    document.querySelectorAll('.visibility-select').forEach(select => {change_visibility(select)});

});

function delete_project(btn) {
    btn.addEventListener('click', function (event) {
        event.preventDefault();
        const projectId = this.dataset.id;
        const projectRow = this.closest('tr');
        const projectTitle = projectRow.querySelector('.project-title').textContent;

        if (confirm(`Are you sure you want to delete "${projectTitle}"? This action cannot be undone.`)) {
            this.innerHTML = '<i class="bi bi-hourglass-split"></i>';
            this.disabled = true;

            fetch(`/project/${projectId}/delete/`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    projectRow.style.transition = 'opacity 0.3s ease';
                    projectRow.style.opacity = '0';
                    setTimeout(() => {
                        projectRow.remove();
                    }, 300);
                } else {
                    alert('Something went wrong. Please try again.');
                    this.innerHTML = '<i class="bi bi-trash"></i>';
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });
};

function toggle_follow(userId) {
    const btn = document.querySelector('#toggle_follow')

    btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Loading...';
    btn.disabled = true;

    fetch(`user/${userId}/follow/`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        const followerCount = document.getElementById('followers-count');

        if (result.message === 'Followed') {
            followerCount.textContent = result.followers;
            btn.innerHTML = '<i class="bi bi-person-dash me-2"></i>Unfollow';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-danger');
        } else {
            followerCount.textContent = result.followers;
            btn.innerHTML = '<i class="bi bi-person-plus me-2"></i>Follow';
            btn.classList.remove('btn-outline-danger');
            btn.classList.add('btn-primary');
        }
        
        btn.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

function star(btn) {
    btn.addEventListener('click', function (event) {
        event.preventDefault();
        const projectId = this.dataset.id;

        fetch(`/project/${projectId}/star/`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);

            // Update button appearance based on the new star status
            if (result.starred) {
                this.classList.replace('btn-outline-secondary', 'btn-warning');
                this.querySelector('i').classList.replace('bi-star', 'bi-star-fill');
            } else {
                this.classList.replace('btn-warning', 'btn-outline-secondary');
                this.querySelector('i').classList.replace('bi-star-fill', 'bi-star');
            }
            
            // Update only the star count on this specific button
            const countElement = document.querySelector('#star-count');
            if (countElement) {
                countElement.textContent = result.count;
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
    });
};

function review() {
    project_id = document.getElementById('review-btn').dataset.id;
    content = document.getElementById('review').value;

    fetch(`/project/${project_id}/reviews/`, {
        method: 'POST',
        body: JSON.stringify({
            content: content,
        })
    })
    .then(resposne => resposne.json())
    .then(result => {
        console.log(result);
        document.getElementById('review').value = '';
        window.location.reload();
    })
    .catch(error => {
        console.log(error);
    });
};

function upload_photo() {
    const image = document.querySelector('#photo-upload')

    // Create FormData object to properly send the image file
    const formData = new FormData();
    formData.append('photo', image.files[0]);

    fetch('user/update_photo/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);

        // Refresh the image to show the new upload
        document.getElementById('profile-image').src = URL.createObjectURL(image.files[0]);
    })
    .catch(error => {
        console.log('Error', error);
    });
};

function change_visibility(select) {
    select.addEventListener('change', function() {
        if(confirm('Confirm your request for project visibility')) {
            
            const projectId = this.dataset.id;
            fetch(`/project/${projectId}/visibility/`, {
                method: 'PUT',
                body: JSON.stringify({
                    visibility: this.value
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                
                const publicOption = this.querySelector('option[value="public"]');
                const privateOption = this.querySelector('option[value="private"]');
                if (result['is_public']) {
                    publicOption.selected = true;
                    publicOption.disabled = true;
                    privateOption.disabled = false;
                } else {
                    privateOption.selected = true;
                    privateOption.disabled = true;
                    publicOption.disabled = false;
                }
            })
            .catch(error => {
                console.log('Error:', error);
            })
        } else {
            window.location.reload();
        }
    });
};