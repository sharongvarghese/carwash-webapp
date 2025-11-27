// Confirm before delete in admin
document.addEventListener("click", function (e) {
  if (e.target.matches(".btn-delete")) {
    const ok = confirm("Are you sure you want to delete this item?");
    if (!ok) {
      e.preventDefault();
    }
  }
});

// Smooth scroll for internal nav links
document.querySelectorAll('a.nav-link[href*="#"]').forEach((link) => {
  link.addEventListener("click", function (e) {
    const href = this.getAttribute("href");
    if (href.startsWith("#")) {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        window.scrollTo({
          top: target.offsetTop - 70,
          behavior: "smooth",
        });
      }
    }
  });
});
