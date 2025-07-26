const foodImages = document.querySelector('.food-images');
const nextButton = document.getElementById('next-button');
const prevButton = document.getElementById('prev-button');
const scrollAmount = 410;

nextButton.addEventListener('click', () => {
    foodImages.scrollTo({
        left: scrollAmount,
        behavior: 'smooth'
    });
});

prevButton.addEventListener('click', () => {
    foodImages.scrollTo({
        left: 0,
        behavior: 'smooth'
    });
});

const images = document.querySelectorAll('.enlargeable-image');
const modal = document.getElementById('imageModal');
const modalImg = document.getElementById('modal-image');
const modalPrevBtn = document.querySelector('.modal-prev');
const modalNextBtn = document.querySelector('.modal-next');
const closeBtn = document.querySelector('.close');
let currentImageIndex = 0;
let allImageSources = [];

images.forEach(image => {
    allImageSources.push(image.src);
});

images.forEach((image, index) => {
    image.addEventListener('click', () => {
        modal.style.display = 'block';
        modalImg.src = image.src;
        currentImageIndex = allImageSources.indexOf(image.src);
    });
});

closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

modalPrevBtn.addEventListener('click', () => {
    currentImageIndex = (currentImageIndex - 1 + allImageSources.length) % allImageSources.length;
    modalImg.src = allImageSources[currentImageIndex];
});

modalNextBtn.addEventListener('click', () => {
    currentImageIndex = (currentImageIndex + 1) % allImageSources.length;
    modalImg.src = allImageSources[currentImageIndex];
});

window.addEventListener('click', (event) => {
    if (event.target == modal) {
        modal.style.display = "none";
    }
});
