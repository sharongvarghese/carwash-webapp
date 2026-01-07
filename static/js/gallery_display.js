document.addEventListener("DOMContentLoaded", () => {

  const slides = document.querySelectorAll(".gallery-slide");
  const nextBtn = document.querySelector(".gallery-nav.next");
  const prevBtn = document.querySelector(".gallery-nav.prev");

  if (slides.length <= 1) return;

  let current = 0;
  let timer;

  function showSlide(index) {
    slides[current].classList.remove("active");
    current = (index + slides.length) % slides.length;
    slides[current].classList.add("active");
  }

  function startAuto() {
    timer = setInterval(() => {
      showSlide(current + 1);
    }, 4000);
  }

  function resetAuto() {
    clearInterval(timer);
    startAuto();
  }

  nextBtn.addEventListener("click", () => {
    showSlide(current + 1);
    resetAuto();
  });

  prevBtn.addEventListener("click", () => {
    showSlide(current - 1);
    resetAuto();
  });

  startAuto();
});
