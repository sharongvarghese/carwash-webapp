/* ====================================================
      AUTO-DISMISS FLASH MESSAGES
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const flashMessages = document.querySelectorAll(".alert");
  
  flashMessages.forEach((alert) => {
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease-out";
      alert.style.opacity = "0";
      
      // Remove from DOM after fade out
      setTimeout(() => {
        alert.remove();
      }, 500);
    }, 4000);
    
    // Allow manual close if there's a close button
    const closeBtn = alert.querySelector(".btn-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.transition = "opacity 0.5s ease-out";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      });
    }
  });
});


/* ====================================================
      CONFIRM DELETE (ADMIN)
==================================================== */
document.addEventListener("click", function (e) {
  if (e.target.matches(".btn-delete")) {
    if (!confirm("Are you sure you want to delete this item?")) {
      e.preventDefault();
    }
  }
});

/* ====================================================
      SMOOTH SCROLL LINKS
==================================================== */
document.querySelectorAll('a.nav-link[href*="#"]').forEach((link) => {
  link.addEventListener("click", function (e) {
    const href = this.getAttribute("href");
    if (href.startsWith("#")) {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        window.scrollTo({
          top: target.offsetTop - 70,
          behavior: "smooth"
        });
      }
    }
  });
});


/* ====================================================
      CLICK OUTSIDE HELPER
==================================================== */
function clickOutside(element, callback) {
  document.addEventListener("click", (e) => {
    if (!element.contains(e.target)) callback();
  });
}


/* ====================================================
      PREMIUM DATE PICKER - WITH PERSISTENCE FIX
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const display = document.getElementById("premiumDateDisplay");
  const dropdown = document.getElementById("premiumDateDropdown");
  const selectedText = document.getElementById("selectedDateText");
  const hiddenDate = document.getElementById("booking-date");

  if (!display) return; // Only run on booking page

  let currentDate = new Date();
  let selectedDate = null;

  // RESTORE SELECTED DATE FROM HIDDEN INPUT (FIX FOR FORM ERRORS)
  if (hiddenDate && hiddenDate.value) {
    selectedDate = hiddenDate.value;
    selectedText.textContent = selectedDate;
    selectedText.style.color = "#ffd700";
    
    // Parse the date to set currentDate to the correct month
    const [year, month] = selectedDate.split('-');
    currentDate = new Date(parseInt(year), parseInt(month) - 1, 1);
  }

  function renderCalendar() {
    dropdown.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // HEADER
    const header = document.createElement("div");
    header.className = "calendar-header";
    header.innerHTML = `
      <span id="prevMonth" class="calendar-arrow" aria-label="Previous month">‹</span>
      <span>${currentDate.toLocaleString("en-US", { month: "long" })} ${year}</span>
      <span id="nextMonth" class="calendar-arrow" aria-label="Next month">›</span>
    `;
    dropdown.appendChild(header);

    document.getElementById("prevMonth").addEventListener("click", (e) => {
      e.stopPropagation();
      currentDate.setMonth(month - 1);
      renderCalendar();
    });

    document.getElementById("nextMonth").addEventListener("click", (e) => {
      e.stopPropagation();
      currentDate.setMonth(month + 1);
      renderCalendar();
    });

    // WEEKDAYS
    const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const daysRow = document.createElement("div");
    daysRow.className = "calendar-grid";

    weekdays.forEach((day) => {
      let el = document.createElement("div");
      el.className = "calendar-day";
      el.textContent = day;
      daysRow.appendChild(el);
    });

    dropdown.appendChild(daysRow);

    // DATE GRID
    const grid = document.createElement("div");
    grid.className = "calendar-grid";

    let firstDay = new Date(year, month, 1).getDay();
    let lastDate = new Date(year, month + 1, 0).getDate();

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
      grid.appendChild(document.createElement("div"));
    }

    // Date cells
    for (let d = 1; d <= lastDate; d++) {
      const dateEl = document.createElement("div");
      dateEl.className = "calendar-date";
      dateEl.textContent = d;

      let fullDate = new Date(year, month, d);
      fullDate.setHours(0, 0, 0, 0);
      
      const dateString = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

      // Disable past dates
      if (fullDate < today) {
        dateEl.classList.add("disabled");
      }

      // Disable Sundays
      if (fullDate.getDay() === 0) {
        dateEl.classList.add("disabled");
      }

      // Highlight today
      if (fullDate.getTime() === today.getTime()) {
        dateEl.classList.add("today");
      }

      // Highlight selected date
      if (selectedDate === dateString) {
        dateEl.classList.add("selected");
      }

      dateEl.addEventListener("click", (e) => {
        e.stopPropagation();

        if (dateEl.classList.contains("disabled")) return;

        // Remove previous selection
        grid.querySelectorAll('.calendar-date').forEach(el => {
          el.classList.remove('selected');
        });

        // Set new selection
        dateEl.classList.add('selected');
        selectedDate = dateString;
        selectedText.textContent = dateString;
        selectedText.style.color = "#ffd700";
        hiddenDate.value = dateString;

        // Remove error styling if present
        display.removeAttribute('data-error');
        display.style.borderColor = "rgba(255, 215, 0, 0.2)";

        dropdown.style.display = "none"; // CLOSE after select
      });

      grid.appendChild(dateEl);
    }

    dropdown.appendChild(grid);
  }

  renderCalendar();

  // OPEN/CLOSE PICKER
  display.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = dropdown.style.display === "block";
    dropdown.style.display = isVisible ? "none" : "block";
  });

  // CLOSE ON OUTSIDE CLICK
  clickOutside(display, () => {
    dropdown.style.display = "none";
  });
});


/* ====================================================
      PREMIUM TIME PICKER - WITH PERSISTENCE FIX
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const display = document.getElementById("premiumTimeDisplay");
  const dropdown = document.getElementById("premiumTimeDropdown");
  const hiddenTime = document.getElementById("booking-time");
  const selectedText = document.getElementById("selectedTimeText");

  if (!display) return;

  let selectedTime = null;

  // RESTORE SELECTED TIME FROM HIDDEN INPUT (FIX FOR FORM ERRORS)
  if (hiddenTime && hiddenTime.value) {
    selectedTime = hiddenTime.value;
    selectedText.textContent = selectedTime;
    selectedText.style.color = "#ffd700";
  }

  function generateTimes() {
    dropdown.innerHTML = "";

    // Generate time slots from 6:00 AM to 6:30 PM
    for (let hour = 6; hour <= 18; hour++) {
      for (let min of ["00", "30"]) {
        // Skip 6:30 PM and beyond
        if (hour === 18 && min === "30") break;
        
        let label = `${hour.toString().padStart(2, "0")}:${min}`;

        const opt = document.createElement("div");
        opt.className = "premium-time-option";
        opt.textContent = label;

        // Highlight selected time
        if (selectedTime === label) {
          opt.classList.add('selected');
        }

        opt.addEventListener("click", (e) => {
          e.stopPropagation();

          // Remove previous selection
          dropdown.querySelectorAll('.premium-time-option').forEach(el => {
            el.classList.remove('selected');
          });

          // Set new selection
          opt.classList.add('selected');
          selectedTime = label;
          selectedText.textContent = label;
          selectedText.style.color = "#ffd700";
          hiddenTime.value = label;

          // Remove error styling if present
          display.removeAttribute('data-error');
          display.style.borderColor = "rgba(255, 215, 0, 0.2)";

          dropdown.style.display = "none"; // CLOSE after select
        });

        dropdown.appendChild(opt);
      }
    }
  }

  generateTimes();

  display.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = dropdown.style.display === "block";
    dropdown.style.display = isVisible ? "none" : "block";
  });

  clickOutside(display, () => {
    dropdown.style.display = "none";
  });
});


/* ====================================================
      ADMIN CONTACT INBOX JS
==================================================== */
// SELECT ALL CHECKBOXES
const selectAll = document.getElementById("selectAll");
if (selectAll) {
  selectAll.addEventListener("change", () => {
    document.querySelectorAll(".msg-checkbox").forEach(cb => {
      cb.checked = selectAll.checked;
    });
  });
}

// DELETE SELECTED
const deleteBtn = document.getElementById("deleteBtn");
if (deleteBtn) {
  deleteBtn.addEventListener("click", () => {
    const checked = document.querySelectorAll(".msg-checkbox:checked");

    if (checked.length === 0) {
      alert("Please select at least one message.");
      return;
    }

    if (confirm("Are you sure you want to delete selected messages?")) {
      document.getElementById("deleteForm").submit();
    }
  });
}


/* ====================================================
      PREMIUM GALLERY SLIDER
==================================================== */

document.addEventListener("DOMContentLoaded", () => {

  const slides = document.querySelectorAll(".gallery-slide");
  const leftBtn = document.querySelector(".gallery-arrow.left");
  const rightBtn = document.querySelector(".gallery-arrow.right");
  const dots = document.querySelectorAll(".dot");
  const counterCurrent = document.querySelector(".counter-current");

  // Exit if no gallery found
  if (!slides || slides.length === 0) return;

  let current = 0;
  let autoTimer = null;
  let isTransitioning = false;

  /* ================================
     SHOW SLIDE FUNCTION
  ================================ */
  function showSlide(index) {
    if (isTransitioning) return;
    isTransitioning = true;

    // Remove active class from current slide
    slides[current].classList.remove("active");
    if (dots.length > 0) dots[current].classList.remove("active");

    // Calculate new index (loop around)
    current = (index + slides.length) % slides.length;

    // Add active class to new slide
    slides[current].classList.add("active");
    if (dots.length > 0) dots[current].classList.add("active");

    // Update counter if exists
    if (counterCurrent) {
      counterCurrent.textContent = current + 1;
    }

    // Reset transition lock after animation completes
    setTimeout(() => {
      isTransitioning = false;
    }, 600); // Match CSS transition duration
  }

  /* ================================
     NAVIGATION FUNCTIONS
  ================================ */
  function nextSlide() {
    showSlide(current + 1);
  }

  function prevSlide() {
    showSlide(current - 1);
  }

  /* ================================
     AUTO-PLAY FUNCTIONS
  ================================ */
  function startAutoPlay() {
    if (slides.length <= 1) return;
    stopAutoPlay();
    autoTimer = setInterval(nextSlide, 5000); // 5 seconds
  }

  function stopAutoPlay() {
    if (autoTimer) {
      clearInterval(autoTimer);
      autoTimer = null;
    }
  }

  function resetAutoPlay() {
    stopAutoPlay();
    startAutoPlay();
  }

  /* ================================
     ARROW BUTTON EVENTS
  ================================ */
  if (leftBtn) {
    leftBtn.addEventListener("click", () => {
      prevSlide();
      resetAutoPlay();
    });
  }

  if (rightBtn) {
    rightBtn.addEventListener("click", () => {
      nextSlide();
      resetAutoPlay();
    });
  }

  /* ================================
     DOT NAVIGATION EVENTS
  ================================ */
  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      showSlide(index);
      resetAutoPlay();
    });
  });

  /* ================================
     KEYBOARD NAVIGATION
  ================================ */
  document.addEventListener("keydown", (e) => {
    const gallery = document.querySelector("#gallery");
    if (!gallery) return;

    // Check if gallery is in viewport
    const rect = gallery.getBoundingClientRect();
    const isInView = rect.top < window.innerHeight && rect.bottom > 0;

    if (isInView) {
      if (e.key === "ArrowLeft") {
        prevSlide();
        resetAutoPlay();
      } else if (e.key === "ArrowRight") {
        nextSlide();
        resetAutoPlay();
      }
    }
  });

  /* ================================
     TOUCH/SWIPE SUPPORT
  ================================ */
  let touchStartX = 0;
  let touchEndX = 0;
  const minSwipeDistance = 50;

  const sliderContainer = document.querySelector(".gallery-slider-wrapper");
  
  if (sliderContainer) {
    sliderContainer.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    sliderContainer.addEventListener("touchend", (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, { passive: true });

    function handleSwipe() {
      const swipeDistance = touchStartX - touchEndX;

      if (Math.abs(swipeDistance) > minSwipeDistance) {
        if (swipeDistance > 0) {
          // Swipe left - go to next
          nextSlide();
        } else {
          // Swipe right - go to previous
          prevSlide();
        }
        resetAutoPlay();
      }
    }

    // Pause on hover (desktop)
    sliderContainer.addEventListener("mouseenter", stopAutoPlay);
    sliderContainer.addEventListener("mouseleave", startAutoPlay);
  }

  /* ================================
     PAGE VISIBILITY API
     Pause when tab is hidden
  ================================ */
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      stopAutoPlay();
    } else {
      startAutoPlay();
    }
  });

  /* ================================
     INTERSECTION OBSERVER
     Only auto-play when visible
  ================================ */
  if ('IntersectionObserver' in window) {
    const galleryObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          startAutoPlay();
        } else {
          stopAutoPlay();
        }
      });
    }, {
      threshold: 0.5 // 50% of gallery must be visible
    });

    const gallerySection = document.querySelector("#gallery");
    if (gallerySection) {
      galleryObserver.observe(gallerySection);
    }
  } else {
    // Fallback for browsers without IntersectionObserver
    startAutoPlay();
  }

  /* ================================
     PRELOAD IMAGES
     Improve performance
  ================================ */
  function preloadImages() {
    slides.forEach(slide => {
      const images = slide.querySelectorAll('img');
      images.forEach(img => {
        if (!img.complete) {
          const tempImg = new Image();
          tempImg.src = img.src;
        }
      });
    });
  }

  preloadImages();

});


/* ====================================================
      FORM SUBMISSION LOADING STATE
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const bookingForm = document.getElementById("booking-form");
  
  if (bookingForm) {
    bookingForm.addEventListener("submit", function(e) {
      const submitBtn = this.querySelector(".booking-cta-btn");
      
      // Add loading state
      if (submitBtn) {
        submitBtn.classList.add("loading");
        submitBtn.disabled = true;
      }
      
      // If form validation fails, re-enable button after a delay
      setTimeout(() => {
        if (submitBtn) {
          submitBtn.classList.remove("loading");
          submitBtn.disabled = false;
        }
      }, 2000);
    });
  }
});