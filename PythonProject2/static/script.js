function confirmAction(action) {
    let message = '';
    let confirmButtonText = '';

    switch(action) {
        case 'add':
            return true; // Skip confirmation for add action
        case 'update':
            message = 'Are you sure you want to save changes to this review?';
            confirmButtonText = 'Yes, update it!';
            break;
        case 'delete':
            message = 'Are you sure you want to delete this review?';
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
    const forms = document.querySelectorAll('form[onsubmit]');
    forms.forEach((form) => {
        form.addEventListener('submit', async (event) => {
            const actionType = form.getAttribute('onsubmit').match(/'(\w+)'/)[1];
            if (actionType !== 'add') {
                event.preventDefault();
                const isConfirmed = await confirmAction(actionType);
                if (isConfirmed) {
                    form.submit();
                }
            }
        });
    });
});
