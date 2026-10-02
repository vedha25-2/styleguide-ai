/**
 * StyleGuide AI - Main Frontend UI Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle with LocalStorage
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const currentTheme = localStorage.getItem('styleguide_theme') || 'light';
  
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    if (themeToggleBtn) {
      themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      const newTheme = isDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('styleguide_theme', newTheme);
      themeToggleBtn.innerHTML = newTheme === 'dark' 
        ? '<i class="fa-solid fa-sun"></i>' 
        : '<i class="fa-solid fa-moon"></i>';
    });
  }

  // Hamburger Sidebar Drawer
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const sidebar = document.getElementById('appSidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function toggleSidebar() {
    if (sidebar) {
      sidebar.classList.toggle('show');
    }
    if (sidebarOverlay) {
      sidebarOverlay.classList.toggle('show');
    }
  }

  if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', toggleSidebar);
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', toggleSidebar);
  }

  // Password Visibility Toggle
  const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
  togglePasswordBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const targetInput = document.querySelector(this.getAttribute('data-target'));
      if (targetInput) {
        const isPassword = targetInput.type === 'password';
        targetInput.type = isPassword ? 'text' : 'password';
        this.innerHTML = isPassword 
          ? '<i class="fa-regular fa-eye-slash"></i>' 
          : '<i class="fa-regular fa-eye"></i>';
      }
    });
  });

  // Auto-dismiss Flash Alerts after 5 seconds
  const autoDismissAlerts = document.querySelectorAll('.alert-dismissible');
  autoDismissAlerts.forEach(alert => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {
        alert.style.display = 'none';
      }
    }, 5000);
  });
});

// Global Toast / Notice Helper
function showToastNotification(message, type = 'info') {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;

  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'primary'} border-0 show`;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  toastContainer.appendChild(toastEl);
  setTimeout(() => toastEl.remove(), 4000);
}
