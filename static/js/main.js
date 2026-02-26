/* ================================================
   LIZ WEB - Main JavaScript
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {

    // ---- Auto-dismiss alerts after 5 seconds ----
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ---- Set min date for date inputs to today ----
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(function(input) {
        if (!input.value) {
            input.setAttribute('min', today);
        }
    });

    // ============================================
    // PASSWORD VISIBILITY TOGGLE (Eye Icon)
    // Works on Login, Register, Create Staff — any
    // page with input[type="password"] fields
    // ============================================
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(function(input) {
        // Wrap the input in a relative div
        const wrapper = document.createElement('div');
        wrapper.className = 'password-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // Create the eye toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle-btn';
        toggleBtn.setAttribute('tabindex', '-1');
        toggleBtn.setAttribute('title', 'Show/Hide password');
        toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
        wrapper.appendChild(toggleBtn);

        // Click to toggle between password and text
        toggleBtn.addEventListener('click', function() {
            const icon = toggleBtn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'bi bi-eye';
            } else {
                input.type = 'password';
                icon.className = 'bi bi-eye-slash';
            }
            input.focus();
        });
    });

});