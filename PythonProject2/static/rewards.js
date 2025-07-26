document.addEventListener('DOMContentLoaded', function() {
    const progressIndicator = document.querySelector('.progress-indicator');
    const greyPath = document.querySelector('.grey-path');
    const greenPath = document.querySelector('.green-path');
    const pointsDisplay = document.getElementById('points-display');
    const membershipLevelDisplay = document.querySelector('.member-info .level b span');
    const redeemButtons = document.querySelectorAll('.redeem-button');

    let pointsBalance = parseInt(pointsDisplay.textContent);

    // Level Thresholds (should match the ones in your Flask app)
    const levelThresholds = {
        "Bronze": 0,
        "Silver": 1000,
        "Gold": 1500,
        "Platinum": 2000
    };

    const maxPoints = levelThresholds["Platinum"]; // Assuming Platinum is the highest level

    // Set up progress indicator
    const radius = greenPath.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    greenPath.style.strokeDasharray = `${circumference} ${circumference}`;
    updateProgress(pointsBalance);

    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    document.body.appendChild(tooltip);

    function showTooltip(event, text) {
        tooltip.textContent = text;
        tooltip.style.display = 'block';
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
    }

    function hideTooltip() {
        tooltip.style.display = 'none';
    }

    function getCurrentLevel(points) {
        let currentLevel = "Bronze";
        for (let [level, threshold] of Object.entries(levelThresholds)) {
            if (points >= threshold) {
                currentLevel = level;
            } else {
                break;
            }
        }
        return currentLevel;
    }

    function getNextLevel(currentPoints) {
        for (let [level, threshold] of Object.entries(levelThresholds)) {
            if (currentPoints < threshold) {
                return [level, threshold - currentPoints];
            }
        }
        return ['Max Level', 0];
    }

    function updateProgress(points) {
        const progressPercentage = (points / maxPoints) * 100;
        const offset = circumference - (progressPercentage / 100) * circumference;
        greenPath.style.strokeDashoffset = offset;

        // Update membership level
        const newLevel = getCurrentLevel(points);
        membershipLevelDisplay.textContent = newLevel;

        // Update points display
        pointsDisplay.textContent = points;
    }

    // Hover functionality for progress indicator
    greyPath.addEventListener('mouseover', (event) => {
        const [nextLevel, pointsNeeded] = getNextLevel(pointsBalance);
        showTooltip(event, `${pointsNeeded} points to ${nextLevel}`);
    });

    greyPath.addEventListener('mouseout', hideTooltip);

    greenPath.addEventListener('mouseover', (event) => {
        showTooltip(event, `Current points: ${pointsBalance}`);
    });

    greenPath.addEventListener('mouseout', hideTooltip);

    // Redeem functionality
    redeemButtons.forEach(button => {
        button.addEventListener('click', function() {
            const offerId = this.getAttribute('data-offer-id');
            const offerPoints = parseInt(this.getAttribute('data-offer-points'));
            const offerTitle = this.closest('.offer-card').querySelector('h3').textContent;

            Swal.fire({
                title: 'Confirm Redemption',
                text: `Are you sure you want to redeem "${offerTitle}" for ${offerPoints} points?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, redeem it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    redeemOffer(offerId, offerPoints);
                }
            });
        });
    });

    function redeemOffer(offerId, offerPoints) {
        fetch('/redeem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ offer_id: offerId, offer_points: offerPoints }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pointsBalance = data.new_balance;
                updateProgress(pointsBalance);
                Swal.fire({
                    title: 'Redeemed!',
                    text: 'Your voucher has been redeemed successfully.',
                    icon: 'success',
                    confirmButtonColor: '#3085d6'
                });
            } else {
                Swal.fire({
                    title: 'Error!',
                    text: data.message,
                    icon: 'error',
                    confirmButtonColor: '#3085d6'
                });
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error!',
                text: 'An error occurred while redeeming the voucher.',
                icon: 'error',
                confirmButtonColor: '#3085d6'
            });
        });
    }
});