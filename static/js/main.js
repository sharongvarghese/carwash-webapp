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




/* ====================================================
      PREMIUM GOLD × BLACK CALENDAR
==================================================== */

document.addEventListener("DOMContentLoaded", () => {
    
  const display = document.getElementById("premiumDateDisplay");
  const dropdown = document.getElementById("premiumDateDropdown");
  const selectedText = document.getElementById("selectedDateText");
  const hiddenDate = document.getElementById("hiddenDateField");

  let currentDate = new Date();

  function renderCalendar() {
      dropdown.innerHTML = "";

      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();

      const firstDay = new Date(year, month, 1).getDay();
      const lastDate = new Date(year, month + 1, 0).getDate();
      const today = new Date();

      // HEADER
      const header = document.createElement("div");
      header.className = "calendar-header";

      header.innerHTML = `
          <span class="calendar-arrow" id="prevMonth">⟨</span>
          <span>${currentDate.toLocaleString("en-US", { month: "long" })} ${year}</span>
          <span class="calendar-arrow" id="nextMonth">⟩</span>
      `;

      dropdown.appendChild(header);

      document.getElementById("prevMonth")?.addEventListener("click", () => {
          currentDate.setMonth(currentDate.getMonth() - 1);
          renderCalendar();
      });

      document.getElementById("nextMonth")?.addEventListener("click", () => {
          currentDate.setMonth(currentDate.getMonth() + 1);
          renderCalendar();
      });

      // WEEKDAYS
      const daysRow = document.createElement("div");
      daysRow.className = "calendar-grid";
      const days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
      days.forEach(d => {
          const el = document.createElement("div");
          el.className = "calendar-day";
          el.textContent = d;
          daysRow.appendChild(el);
      });
      dropdown.appendChild(daysRow);

      // DATES GRID
      const dateGrid = document.createElement("div");
      dateGrid.className = "calendar-grid";

      // Empty spaces for first-day alignment
      for (let i = 0; i < firstDay; i++) {
          dateGrid.appendChild(document.createElement("div"));
      }

      for (let day = 1; day <= lastDate; day++) {
          const d = document.createElement("div");
          d.className = "calendar-date";
          d.textContent = day;

          const fullDate = new Date(year, month, day);

          // Disable past dates
          if (fullDate < new Date().setHours(0,0,0,0)) {
              d.classList.add("disabled");
          }

          // Disable Sundays
          if (fullDate.getDay() === 0) {
              d.classList.add("disabled");
          }

          // Today highlight
          if (day === today.getDate() &&
              month === today.getMonth() &&
              year === today.getFullYear()) {
              d.classList.add("today");
          }

          // Click handler
          d.addEventListener("click", () => {
              selectedText.textContent =
                `${year}-${String(month+1).padStart(2,"0")}-${String(day).padStart(2,"0")}`;

              hiddenDate.value = selectedText.textContent;

              dropdown.style.display = "none";
          });

          dateGrid.appendChild(d);
      }

      dropdown.appendChild(dateGrid);
  }

  // Initial Calendar Render
  renderCalendar();

  // Toggle dropdown
  display.addEventListener("click", () => {
      dropdown.style.display =
        dropdown.style.display === "block" ? "none" : "block";
  });

  // Close when clicked outside
  document.addEventListener("click", (e) => {
      if (!display.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.style.display = "none";
      }
  });

});

// PREMIUM TIME PICKER (6 AM – 6 PM)
document.addEventListener("DOMContentLoaded", () => {

  const display = document.getElementById("premiumTimeDisplay");
  const dropdown = document.getElementById("premiumTimeDropdown");
  const selectedText = document.getElementById("selectedTimeText");
  const hiddenTime = document.getElementById("hiddenTimeField");

  // Generate time slots
  const generateTimes = () => {
    dropdown.innerHTML = "";
    for (let hour = 6; hour <= 18; hour++) {
      for (let min of ["00", "30"]) {
        let h = hour < 10 ? "0" + hour : hour;
        let label = `${h}:${min}`;
        let opt = document.createElement("div");
        opt.className = "premium-time-option";
        opt.textContent = label;

        opt.addEventListener("click", () => {
          selectedText.textContent = label;
          hiddenTime.value = label;
          dropdown.style.display = "none";
        });

        dropdown.appendChild(opt);
      }
    }
  };

  generateTimes();

  // Toggle dropdown
  display.addEventListener("click", () => {
    dropdown.style.display =
      dropdown.style.display === "block" ? "none" : "block";
  });

  // Close when clicking outside
  document.addEventListener("click", (e) => {
    if (!display.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });

});


