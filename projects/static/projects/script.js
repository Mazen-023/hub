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

    // Add star to a project
    document.querySelectorAll('.star').forEach(button => { star(button) });

});

function delete_project(btn) {
    btn.addEventListener('click', function (event) {
        event.preventDefault();
        const projectId = this.dataset.id;
        const projectRow = this.closest('tr');
        const projectTitle = projectRow.querySelector('.project-title').textContent;

        if (confirm(`Are you sure you want to delete "${projectTitle}"? This action cannot be undone.`)) {
            // Add loading state
            this.innerHTML = '<i class="bi bi-hourglass-split"></i>';
            this.disabled = true;

            fetch(`/delete/${projectId}/`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    // Fade out and remove the row
                    projectRow.style.transition = 'opacity 0.3s ease';
                    projectRow.style.opacity = '0';
                    setTimeout(() => {
                        projectRow.remove();
                        // Update project count
                        const badge = document.querySelector('.card-header .badge');
                        if (badge) {
                            const currentCount = parseInt(badge.textContent.split(' ')[0]);
                            badge.textContent = `${currentCount - 1} total`;
                        }
                    }, 300);
                } else {
                    alert('Something went wrong. Please try again.');
                    // Reset button
                    this.innerHTML = '<i class="bi bi-trash"></i>';
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please check the console.');
                // Reset button
                this.innerHTML = '<i class="bi bi-trash"></i>';
                this.disabled = false;
            });
        }
    });
}

function toggle_follow(userId) {
    const btn = document.querySelector('#toggle_follow')

    // Add loading state
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
}

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
}