/* ====================================================
   PACKAGE BOOKING - COMPLETE JAVASCRIPT
==================================================== */

document.addEventListener("DOMContentLoaded", () => {

  /* ====================================================
     AUTO-DISMISS FLASH MESSAGES
  ==================================================== */
  const flashMessages = document.querySelectorAll(".alert");
  
  flashMessages.forEach((alert) => {
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease-out";
      alert.style.opacity = "0";
      
      // Remove from DOM after fade out
      setTimeout(() => {
        alert.remove();
      }, 500);
    }, 5000);
    
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

  /* ====================================================
     FORM VALIDATION & SUBMISSION
  ==================================================== */
  const bookingForm = document.querySelector(".booking-form");
  
  if (bookingForm) {
    // Phone number formatting
    const phoneInput = bookingForm.querySelector('input[name="phone"]');
    if (phoneInput) {
      phoneInput.addEventListener('input', function(e) {
        // Remove non-numeric characters except +, -, (, ), and spaces
        this.value = this.value.replace(/[^0-9+\-() ]/g, '');
      });
      
      // Validate phone on blur
      phoneInput.addEventListener('blur', function() {
        const value = this.value.replace(/[^0-9]/g, '');
        if (value.length < 8) {
          this.classList.add('is-invalid');
          showError(this, 'Phone number must be at least 8 digits');
        } else {
          this.classList.remove('is-invalid');
          clearError(this);
        }
      });
    }

    // Email validation on blur
    const emailInput = bookingForm.querySelector('input[name="email"]');
    if (emailInput) {
      emailInput.addEventListener('blur', function() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.value)) {
          this.classList.add('is-invalid');
          showError(this, 'Please enter a valid email address');
        } else {
          this.classList.remove('is-invalid');
          clearError(this);
        }
      });
    }

    // Full name validation
    const nameInput = bookingForm.querySelector('input[name="full_name"]');
    if (nameInput) {
      nameInput.addEventListener('blur', function() {
        if (this.value.trim().length < 2) {
          this.classList.add('is-invalid');
          showError(this, 'Please enter your full name');
        } else {
          this.classList.remove('is-invalid');
          clearError(this);
        }
      });
    }

    // Form submission handler
    bookingForm.addEventListener('submit', function(e) {
      const submitBtn = this.querySelector('.booking-cta-btn');
      
      // Check for any validation errors
      const invalidInputs = this.querySelectorAll('.is-invalid');
      if (invalidInputs.length > 0) {
        e.preventDefault();
        invalidInputs[0].focus();
        return false;
      }
      
      // Add loading state
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Processing...';
        
        // Reset button after 10 seconds (in case of slow server)
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 10000);
      }
    });

    // Clear validation on input
    const allInputs = bookingForm.querySelectorAll('.premium-input');
    allInputs.forEach(input => {
      input.addEventListener('input', function() {
        if (this.classList.contains('is-invalid')) {
          this.classList.remove('is-invalid');
          clearError(this);
        }
      });
    });
  }

  /* ====================================================
     HELPER FUNCTIONS
  ==================================================== */
  function showError(input, message) {
    clearError(input);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
  }

  function clearError(input) {
    const errorDiv = input.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  /* ====================================================
     SMOOTH SCROLL FOR HASH LINKS
  ==================================================== */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href !== '') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          const offsetTop = target.offsetTop - 80;
          window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  /* ====================================================
     INPUT FOCUS ANIMATIONS
  ==================================================== */
  const premiumInputs = document.querySelectorAll('.premium-input');
  premiumInputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('input-focused');
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('input-focused');
    });
  });

  /* ====================================================
     PREVENT DOUBLE FORM SUBMISSION
  ==================================================== */
  let formSubmitted = false;
  if (bookingForm) {
    bookingForm.addEventListener('submit', function() {
      if (formSubmitted) {
        return false;
      }
      formSubmitted = true;
      
      // Reset after 5 seconds
      setTimeout(() => {
        formSubmitted = false;
      }, 5000);
    });
  }

  /* ====================================================
     MOBILE VIEWPORT HEIGHT FIX
  ==================================================== */
  function setViewportHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  
  setViewportHeight();
  window.addEventListener('resize', setViewportHeight);
  window.addEventListener('orientationchange', setViewportHeight);

  /* ====================================================
     LAZY LOAD IMAGES
  ==================================================== */
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }

  /* ====================================================
     ACCESSIBILITY: KEYBOARD NAVIGATION
  ==================================================== */
  document.addEventListener('keydown', function(e) {
    // Escape key to close modals/dropdowns
    if (e.key === 'Escape') {
      const alerts = document.querySelectorAll('.alert');
      alerts.forEach(alert => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
      });
    }
  });

  /* ====================================================
     PERFORMANCE: DEBOUNCE RESIZE EVENTS
  ==================================================== */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  const handleResize = debounce(function() {
    // Handle resize-specific logic here
    setViewportHeight();
  }, 250);

  window.addEventListener('resize', handleResize);

  /* ====================================================
     CONSOLE LOG - BOOKING PAGE LOADED
  ==================================================== */
  console.log('✅ Package Booking Page Loaded Successfully');

});

/* ====================================================
   GLOBAL UTILITY FUNCTIONS
==================================================== */

// Click outside handler
function clickOutside(element, callback) {
  document.addEventListener('click', function handler(e) {
    if (element && !element.contains(e.target)) {
      callback();
    }
  });
}

// Format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

// Validate email
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Validate phone
function isValidPhone(phone) {
  const cleaned = phone.replace(/[^0-9]/g, '');
  return cleaned.length >= 8 && cleaned.length <= 15;
}