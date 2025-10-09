document.addEventListener('DOMContentLoaded', function() {
    star();
});

function star() {
    document.querySelectorAll('.star').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const projectId = this.dataset.id;
            
            fetch(`/star/${projectId}/`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
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
    });
}