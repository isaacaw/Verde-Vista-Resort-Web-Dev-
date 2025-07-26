// Function to confirm actions (update or delete)
function confirmAction(action) {
    let message = '';
    let confirmButtonText = '';

    switch (action) {
        case 'update':
            message = 'Are you sure you want to save changes to this booking?';
            confirmButtonText = 'Yes, update it!';
            break;
        case 'delete':
            message = 'Are you sure you want to delete this booking?';
            confirmButtonText = 'Yes, delete it!';
            break;
        default:
            message = 'Are you sure you want to perform this action?';
            confirmButtonText = 'Yes, proceed!';
    }

    return Swal.fire({
        title: 'Confirm Action',
        text: message,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: confirmButtonText
    }).then((result) => {
        return result.isConfirmed;
    });
}

// Attach event listeners to forms
document.addEventListener('DOMContentLoaded', () => {
    // Handle delete links in the cart
    const deleteLinks = document.querySelectorAll('a[href*="remove_from_cart"]');
    deleteLinks.forEach((link) => {
        link.addEventListener('click', async (event) => {
            event.preventDefault(); // Prevent the default link behavior
            const isConfirmed = await confirmAction('delete');
            if (isConfirmed) {
                window.location.href = link.href; // Redirect to the delete URL
            }
        });
    });

    // Handle update forms in the edit_cart page
    const updateForm = document.querySelector('form[method="POST"]');
    if (updateForm) {
        updateForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent the default form submission
            const isConfirmed = await confirmAction('update');
            if (isConfirmed) {
                updateForm.submit(); // Submit the form if confirmed
            }
        });
    }
});