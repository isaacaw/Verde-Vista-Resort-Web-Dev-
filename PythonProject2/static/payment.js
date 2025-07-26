document.getElementById('payment-method').addEventListener('change', function () {
    const paymentMethod = this.value;
    document.querySelectorAll('.payment-details').forEach((div) => {
        div.style.display = 'none';
    });
    if (paymentMethod) {
        document.getElementById(`${paymentMethod}-details`).style.display = 'block';
    }
});

function validatePayment() {
    const paymentMethod = document.getElementById('payment-method').value;
    const errorMessages = [];

    document.querySelectorAll('.error-message').forEach((div) => {
        div.textContent = '';
    });

    if (!paymentMethod) {
        errorMessages.push('Please select a payment method.');
    }

    if (paymentMethod === 'credit-card') {
        const cardNumber = document.getElementById('card-number').value;
        const expiryDate = document.getElementById('expiry-date').value;
        const cvv = document.getElementById('cvv').value;

        if (!cardNumber || !/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) {
            document.getElementById('card-number-error').textContent = 'Please enter a valid 16-digit card number.';
            errorMessages.push('Invalid card number.');
        }
        if (!expiryDate || !/^\d{2}\/\d{2}$/.test(expiryDate)) {
            document.getElementById('expiry-date-error').textContent = 'Please enter a valid expiry date (MM/YY).';
            errorMessages.push('Invalid expiry date.');
        }
        if (!cvv || !/^\d{3}$/.test(cvv)) {
            document.getElementById('cvv-error').textContent = 'Please enter a valid 3-digit CVV.';
            errorMessages.push('Invalid CVV.');
        }
    }

    if (errorMessages.length > 0) {
        return false;
    }


    alert('Payment successful! Thank you for your purchase.');
    return true;
}