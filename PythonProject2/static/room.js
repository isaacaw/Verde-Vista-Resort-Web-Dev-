function openModal(roomId) {
    document.getElementById(`modal-${roomId}`).style.display = 'block';
}

function closeModal(roomId) {
    document.getElementById(`modal-${roomId}`).style.display = 'none';
}

window.onclick = function (event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach((modal) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};

function prevImage(roomId) {
    const roomImages = document.querySelector(`#modal-${roomId} .room-images`);
    roomImages.scrollBy({ left: -200, behavior: 'smooth' });
}

function nextImage(roomId) {
    const roomImages = document.querySelector(`#modal-${roomId} .room-images`);
    roomImages.scrollBy({ left: 200, behavior: 'smooth' });
}