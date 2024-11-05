

// Scripts fpr console select in games edit view

class ConsoleSelector {
    constructor() {
        this.init();
    }

    init() {
        this.addConsoleClickHandlers();
        this.preventTextSelection();
    }

    handleConsoleSelection(checkbox) {
        const consoleOption = checkbox.closest('.console-option');

        // Simply toggle the selected state
        if (checkbox.checked) {
            consoleOption.classList.add('selected');
        } else {
            consoleOption.classList.remove('selected');
        }
    }

    addConsoleClickHandlers() {
        document.querySelectorAll('.console-option').forEach(option => {
            option.addEventListener('click', (event) => {
                // Prevent default only if clicking the label/div (not the checkbox)
                if (!event.target.classList.contains('console-checkbox')) {
                    event.preventDefault();

                    const checkbox = option.querySelector('.console-checkbox');
                    checkbox.checked = !checkbox.checked;
                    this.handleConsoleSelection(checkbox);
                }
            });

            // Handle direct checkbox changes
            const checkbox = option.querySelector('.console-checkbox');
            checkbox.addEventListener('change', () => {
                this.handleConsoleSelection(checkbox);
            });
        });
    }

    preventTextSelection() {
        document.querySelectorAll('.console-label').forEach(label => {
            label.addEventListener('mousedown', (e) => {
                e.preventDefault();
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ConsoleSelector();
});


// Scripts for Custom file upload input
//
// function handleImageUpload(input) {
//     if (input.files && input.files[0]) {
//         const wrapper = document.getElementById(`wrapper_${input.id}`);
//         const file = input.files[0];
//         const reader = new FileReader();
//
//         reader.onload = function(e) {
//             // Create new preview container
//             wrapper.innerHTML = `
//                 <div class="image-preview-container">
//                     <img src="${e.target.result}" alt="Selected image" class="image-preview">
//                     <div class="image-actions">
//                         <label class="upload-btn" for="${input.id}">Change</label>
//                         <button type="button" class="clear-btn" onclick="clearImage('${input.id}')">Clear</button>
//                     </div>
//                 </div>
//                 <input type="file"
//                        name="${input.name}"
//                        id="${input.id}"
//                        class="image-input"
//                        style="display: none;">
//                 <input type="checkbox"
//                        name="${input.name}-clear"
//                        id="${input.id}-clear"
//                        class="clear-checkbox"
//                        style="display: none;">
//             `;
//         };
//
//         reader.readAsDataURL(file);
//     }
// }
//
// function clearImage(inputId) {
//     const wrapper = document.getElementById(`wrapper_${inputId}`);
//     const clearCheckbox = document.getElementById(`${inputId}-clear`);
//
//     // Check the hidden clear checkbox
//     if (clearCheckbox) {
//         clearCheckbox.checked = true;
//     }
//
//     // Reset the file input
//     const fileInput = document.getElementById(inputId);
//     if (fileInput) {
//         fileInput.value = '';
//     }
//
//     // Update UI to show upload button only
//     wrapper.innerHTML = `
//         <div class="upload-container">
//             <label class="upload-btn" for="${inputId}">Upload Picture</label>
//         </div>
//         <input type="file"
//                name="${fileInput.name}"
//                id="${inputId}"
//                class="image-input"
//                style="display: none;">
//         <input type="checkbox"
//                name="${fileInput.name}-clear"
//                id="${inputId}-clear"
//                class="clear-checkbox"
//                checked
//                style="display: none;">
//     `;
// }


// Enhanced image upload handling
function handleImageUpload(input) {
    if (input.files && input.files[0]) {
        const wrapper = document.getElementById(`wrapper_${input.id}`);
        const file = input.files[0];
        const reader = new FileReader();

        // Store all original input attributes
        const originalName = input.name;
        const originalRequired = input.hasAttribute('required');
        const originalAccept = input.accept;
        const originalId = input.id;

        reader.onload = function(e) {
            wrapper.innerHTML = `
                <div class="image-preview-container">
                    <img src="${e.target.result}" alt="Selected image" class="image-preview">
                    <div class="image-actions">
                        <label for="${originalId}" class="button primary small">Change</label>
                        <button type="button" class="button small" onclick="clearImage('${originalId}')">Clear</button>
                    </div>
                </div>
                <input type="file"
                       name="${originalName}"
                       id="${originalId}"
                       class="image-input"
                       onchange="handleImageUpload(this)"
                       accept="${originalAccept}"
                       ${originalRequired ? 'required' : ''}
                       style="display: none;">
                <input type="checkbox"
                       name="${originalName}-clear"
                       id="${originalId}-clear"
                       class="clear-checkbox"
                       style="display: none;">
            `;

            // Re-attach the file to the new input
            const newInput = document.getElementById(originalId);

            // Create a new FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            newInput.files = dataTransfer.files;
        };

        reader.readAsDataURL(file);
    }
}

function clearImage(inputId) {
    const wrapper = document.getElementById(`wrapper_${inputId}`);
    const originalInput = document.getElementById(inputId);

    // Store original input attributes
    const originalName = originalInput.name;
    const originalRequired = originalInput.hasAttribute('required');
    const originalAccept = originalInput.accept;

    wrapper.innerHTML = `
        <div class="upload-container">
            <label for="${inputId}" class="button primary small">Upload Picture</label>
        </div>
        <input type="file"
               name="${originalName}"
               id="${inputId}"
               class="image-input"
               onchange="handleImageUpload(this)"
               accept="${originalAccept}"
               ${originalRequired ? 'required' : ''}
               style="display: none;">
        <input type="checkbox"
               name="${originalName}-clear"
               id="${inputId}-clear"
               class="clear-checkbox"
               checked
               style="display: none;">
    `;
}

// Initialize file inputs when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const fileInputs = document.querySelectorAll('.image-input');
    fileInputs.forEach(input => {
        const originalOnChange = input.onchange;
        input.addEventListener('change', (event) => {
            if (originalOnChange) {
                originalOnChange.call(input, event);
            }
            handleImageUpload(input);
        });
    });
});


// show / hide rating / your rating

document.addEventListener('DOMContentLoaded', function() {
  const currentRatingLinks = document.querySelectorAll('.current-rating a');

  currentRatingLinks.forEach(currentRatingLink => {
    const currentRatingDiv = currentRatingLink.closest('.current-rating');
    const yourRatingDiv = currentRatingDiv.nextElementSibling;
    const hideRatingLink = yourRatingDiv.querySelector('a');

    currentRatingLink.addEventListener('click', (event) => {
      event.preventDefault();
      yourRatingDiv.style.display = 'block';
      currentRatingLink.style.display = 'none';
    });

    hideRatingLink.addEventListener('click', (event) => {
      event.preventDefault();
      yourRatingDiv.style.display = 'none';
      currentRatingLink.style.display = 'block';
    });
  });
});


 // Screenshot delete functionality
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#delete-screenshot').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();

            // Get the screenshot container and its ID
            const container = this.closest('.screenshot-container');
            const screenshotId = container.id.split('-')[1];

            // Change button text and disable it
            const originalText = this.textContent;
            this.textContent = 'Deleting...';
            this.classList.add('disabled');
            this.style.backgroundColor = 'red';

            try {
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                // Send delete request
                const response = await fetch(`/games/screenshot/${screenshotId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json',
                    },
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Wait for 500ms to show the "Deleting..." message
                    await new Promise(resolve => setTimeout(resolve, 500));

                    // Smooth fade out animation
                    container.style.transition = 'opacity 0.3s ease-out';
                    container.style.opacity = '0';

                    // Wait for fade out animation
                    await new Promise(resolve => setTimeout(resolve, 300));

                    // Remove the container and redirect
                    container.remove();
                    window.location.hash = data.redirect_url;
                }
            } catch (error) {
                console.error('Error:', error);
                // Reset button on error
                this.textContent = originalText;
                this.classList.remove('disabled');
                this.style.backgroundColor = '';
            }
        });
    });
});


/* scripts for comments - show/hide more*/
document.addEventListener('DOMContentLoaded', function () {
    const comments = document.querySelectorAll('.comment');
    const showMoreBtn = document.getElementById('show-more-comments');
    const showLessBtn = document.getElementById('show-less-comments');

    // Display only the first 4 comments initially
    if (comments.length > 4) {
        comments.forEach((comment, index) => {
            if (index >= 4) {
                comment.style.display = 'none';
            }
        });

        // Show the "Show all" button
        showMoreBtn.style.display = 'inline-block';

        // Event listener for "Show all" button
        showMoreBtn.addEventListener('click', function (e) {
            e.preventDefault();
            comments.forEach(comment => comment.style.display = 'block'); // Show all comments
            showMoreBtn.style.display = 'none';
            showLessBtn.style.display = 'inline-block';
        });

        // Event listener for "Show less" button
        showLessBtn.addEventListener('click', function (e) {
            e.preventDefault();
            comments.forEach((comment, index) => {
                if (index >= 4) {
                    comment.style.display = 'none'; // Hide comments after the 4th one
                }
            });
            showLessBtn.style.display = 'none';
            showMoreBtn.style.display = 'inline-block';
        });
    }
});


// acroll to the first element with class "error"

// const firstErrorElement = document.querySelector('.error');
// if (firstErrorElement) {
//     firstErrorElement.scrollIntoView({ behavior: 'auto', block: 'center' });
// }


const firstErrorElement = document.querySelector('.error');
if (firstErrorElement) {
    const elementPosition = firstErrorElement.getBoundingClientRect().top + window.pageYOffset;
    const offset = window.innerHeight / 2 - firstErrorElement.offsetHeight / 2; // Centering offset

    window.scrollTo({
        top: elementPosition - offset,
        left: 0,
        behavior: 'auto' // This ensures the scroll is instant
    });
}
