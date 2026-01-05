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
      PREMIUM DATE PICKER (FINAL FIXED VERSION)
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const display = document.getElementById("premiumDateDisplay");
  const dropdown = document.getElementById("premiumDateDropdown");
  const selectedText = document.getElementById("selectedDateText");
  const hiddenDate = document.getElementById("booking-date");

  if (!display) return; // Only run on booking page

  let currentDate = new Date();

  function renderCalendar() {
    dropdown.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const today = new Date();

    // HEADER
    const header = document.createElement("div");
    header.className = "calendar-header";
    header.innerHTML = `
      <span id="prevMonth" class="calendar-arrow">⟨</span>
      <span>${currentDate.toLocaleString("en-US", { month: "long" })} ${year}</span>
      <span id="nextMonth" class="calendar-arrow">⟩</span>
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

    for (let i = 0; i < firstDay; i++) {
      grid.appendChild(document.createElement("div"));
    }

    for (let d = 1; d <= lastDate; d++) {
      const dateEl = document.createElement("div");
      dateEl.className = "calendar-date";
      dateEl.textContent = d;

      let fullDate = new Date(year, month, d);

      if (fullDate < new Date().setHours(0, 0, 0, 0)) {
        dateEl.classList.add("disabled");
      }

      if (fullDate.getDay() === 0) {
        dateEl.classList.add("disabled");
      }

      dateEl.addEventListener("click", (e) => {
        e.stopPropagation();

        if (dateEl.classList.contains("disabled")) return;

        const value = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        selectedText.textContent = value;
        hiddenDate.value = value;

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
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  });

  // CLOSE ON OUTSIDE CLICK
  clickOutside(dropdown, () => (dropdown.style.display = "none"));
});


/* ====================================================
      PREMIUM TIME PICKER (FINAL VERSION)
==================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const display = document.getElementById("premiumTimeDisplay");
  const dropdown = document.getElementById("premiumTimeDropdown");
  const hiddenTime = document.getElementById("booking-time");
  const selectedText = document.getElementById("selectedTimeText");

  if (!display) return;

  function generateTimes() {
    dropdown.innerHTML = "";

    for (let hour = 6; hour <= 18; hour++) {
      for (let min of ["00", "30"]) {
        let label = `${hour.toString().padStart(2, "0")}:${min}`;

        const opt = document.createElement("div");
        opt.className = "premium-time-option";
        opt.textContent = label;

        opt.addEventListener("click", (e) => {
          e.stopPropagation();

          selectedText.textContent = label;
          hiddenTime.value = label;

          dropdown.style.display = "none"; // CLOSE after select
        });

        dropdown.appendChild(opt);
      }
    }
  }

  generateTimes();

  display.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  });

  clickOutside(dropdown, () => (dropdown.style.display = "none"));
});


/* ====================================================
      AJAX BOOKING SUBMISSION (SUPER CLEAN VERSION)
==================================================== */
async function submitBooking(event) {
  event.preventDefault(); // Stop page reload

  const form = document.getElementById("booking-form");
  const formData = new FormData(form);

  // Clear previous errors
  document.querySelectorAll(".text-danger.small").forEach(el => {
    el.textContent = "";
  });

  // Send AJAX request
  const response = await fetch("/booking", {
    method: "POST",
    headers: { "X-Requested-With": "XMLHttpRequest" },
    body: formData
  });

  const data = await response.json();

  if (!data.success) {
    // Show validation errors
    for (let field in data.errors) {
      const errorBox = document.getElementById(`${field}-error`);
      if (errorBox) {
        errorBox.textContent = data.errors[field][0];
      }
    }
    return false;
  }

  // SUCCESS
  alert(data.message);

  // Reset form
  form.reset();

  document.getElementById("selectedDateText").textContent = "Select Date";
  document.getElementById("selectedTimeText").textContent = "Select Time";

  return false;
}


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

/* =====================================
   GALLERY BEFORE / AFTER TRANSITION ONLY
===================================== */

document.addEventListener("DOMContentLoaded", () => {

  const INTERVAL = 3000;

  document
    .querySelectorAll(".gallery-card-overlay")
    .forEach(overlay => {

      // prevent double start
      if (overlay.dataset.started === "true") return;
      overlay.dataset.started = "true";

      const img = overlay.querySelector(".gallery-image-overlay");
      const beforeBadge = overlay.querySelector(".gallery-badge.before");
      const afterBadge = overlay.querySelector(".gallery-badge.after");

      const beforeImg = overlay.dataset.before;
      const afterImg = overlay.dataset.after;

      let showBefore = true;

      setInterval(() => {
        img.style.opacity = 0;

        setTimeout(() => {
          if (showBefore) {
            img.src = afterImg;
            beforeBadge.classList.remove("active");
            afterBadge.classList.add("active");
          } else {
            img.src = beforeImg;
            afterBadge.classList.remove("active");
            beforeBadge.classList.add("active");
          }

          img.style.opacity = 1;
          showBefore = !showBefore;
        }, 400);

      }, INTERVAL);
    });

});



