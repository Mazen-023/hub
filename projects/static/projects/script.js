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
    document.querySelectorAll('.star').forEach(button => { star(button) });

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

            fetch(`/delete/${projectId}/`, {
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

    fetch(`/follow/${userId}/`, {
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

        fetch(`/star/${projectId}/`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(result => {
            // Update the star count
            const star_count = document.querySelector(`.star-count[data-id="${projectId}"]`);
            if (star_count) {
                star_count.innerHTML = result["stars"];
            }

            // Toggle the star icon(s) - check each one separately
            const star_icon1 = document.querySelector(`.star_icon1[data-id="${projectId}"]`);
            if (star_icon1) {
                star_icon1.innerHTML = star_icon1.innerHTML === '⭐' ? '☆' : '⭐';
            }

            const star_icon2 = document.querySelector(`.star_icon2[data-id="${projectId}"]`);
            if (star_icon2) {
                star_icon2.innerHTML = star_icon2.innerHTML === '★' ? '☆' : '★';
            }

            // Toggle button text and style
            if (this.textContent.includes('Star') && !this.textContent.includes('Starred')) {
                this.innerHTML = '<i class="star_icon1" data-id="' + projectId + '">⭐</i> Starred';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-outline-warning');
            } else {
                this.innerHTML = '<i class="star_icon1" data-id="' + projectId + '">☆</i> Star';
                this.classList.remove('btn-outline-warning');
                this.classList.add('btn-outline-secondary');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
};

function review() {
    project_id = document.getElementById('review-btn').dataset.id;
    content = document.getElementById('review').value;

    fetch(`/reviews/${project_id}/`, {
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

    fetch('/update_photo/', {
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