document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------------
    // 1. Preloader fadeout
    // -----------------------------------------------------------------
    const loader = document.getElementById('page-loader');
    if (loader) {
        // Add a slight artificial delay to make the cyberpunk loader feel premium and noticeable
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 600);
    }

    // Show preloader when clicking internal links for clean transitions
    const links = document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript:"])');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                if (loader) {
                    e.preventDefault();
                    loader.classList.remove('hidden');
                    setTimeout(() => {
                        window.location.href = href;
                    }, 250);
                }
            }
        });
    });

    // -----------------------------------------------------------------
    // 2. Mobile Responsive Menu
    // -----------------------------------------------------------------
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
            // Toggle hamburger icon between bars and times (close)
            const icon = navToggle.querySelector('i');
            if (icon) {
                if (navMenu.classList.contains('open')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }

    // -----------------------------------------------------------------
    // 3. Scanner Form Loading State on Submit
    // -----------------------------------------------------------------
    const scanForms = document.querySelectorAll('.scan-form');
    scanForms.forEach(form => {
        form.addEventListener('submit', () => {
            if (loader) {
                const loaderText = loader.querySelector('.loader-text');
                if (loaderText) {
                    loaderText.textContent = "Analyzing threat vectors...";
                }
                loader.classList.remove('hidden');
            }
        });
    });

    // -----------------------------------------------------------------
    // 4. Password Checker - Real-Time Analysis
    // -----------------------------------------------------------------
    const passwordInput = document.getElementById('password-input');
    const togglePasswordBtn = document.getElementById('toggle-password-btn');

    if (passwordInput) {
        const checkLength = document.getElementById('chk-length');
        const checkUpper = document.getElementById('chk-upper');
        const checkLower = document.getElementById('chk-lower');
        const checkNumber = document.getElementById('chk-number');
        const checkSpecial = document.getElementById('chk-special');
        
        const meterBar = document.getElementById('pw-meter-bar');
        const meterStatus = document.getElementById('pw-meter-status');
        const meterPercentage = document.getElementById('pw-meter-percentage');

        const evaluatePassword = () => {
            const pwd = passwordInput.value;
            
            // Rules matching
            const hasLength = pwd.length >= 8;
            const hasUpper = /[A-Z]/.test(pwd);
            const hasLower = /[a-z]/.test(pwd);
            const hasNumber = /[0-9]/.test(pwd);
            const hasSpecial = /[@#$%^&*!_\-+=~]/.test(pwd);

            // Update Checklist UI
            updateChecklistItem(checkLength, hasLength);
            updateChecklistItem(checkUpper, hasUpper);
            updateChecklistItem(checkLower, hasLower);
            updateChecklistItem(checkNumber, hasNumber);
            updateChecklistItem(checkSpecial, hasSpecial);

            // Calculate Score (0 to 5)
            const score = (hasLength ? 1 : 0) + (hasUpper ? 1 : 0) + (hasLower ? 1 : 0) + (hasNumber ? 1 : 0) + (hasSpecial ? 1 : 0);

            // Map Score to UI styles
            let statusText = "Too Short";
            let statusClass = "danger";
            let percent = "10%";

            if (pwd.length > 0) {
                if (score <= 2) {
                    statusText = "Weak";
                    statusClass = "danger";
                    percent = "30%";
                } else if (score <= 4) {
                    statusText = "Medium";
                    statusClass = "warning";
                    percent = "65%";
                } else {
                    statusText = "Strong";
                    statusClass = "safe";
                    percent = "100%";
                }
            } else {
                statusText = "Enter password";
                statusClass = "dark";
                percent = "0%";
            }

            // Update meter styling
            if (meterBar) {
                meterBar.className = `meter-bar-fill ${statusClass}`;
                meterBar.style.width = percent;
            }
            if (meterStatus) {
                meterStatus.textContent = statusText;
                meterStatus.className = `badge ${statusClass}`;
            }
            if (meterPercentage) {
                meterPercentage.textContent = percent;
            }
        };

        // Run evaluation on every keystroke
        passwordInput.addEventListener('input', evaluatePassword);

        // Toggle password character visibility
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', () => {
                const icon = togglePasswordBtn.querySelector('i');
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    if (icon) {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                } else {
                    passwordInput.type = 'password';
                    if (icon) {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            });
        }
    }

    // Helper to toggle icons and css classes on password checkmarks
    function updateChecklistItem(element, isValid) {
        if (!element) return;
        const icon = element.querySelector('i');
        if (isValid) {
            element.classList.add('valid');
            if (icon) {
                icon.className = 'fas fa-check-circle';
            }
        } else {
            element.classList.remove('valid');
            if (icon) {
                icon.className = 'far fa-circle';
            }
        }
    }

    // -----------------------------------------------------------------
    // 5. Interactive Tips Toggle (Privacy Page)
    // -----------------------------------------------------------------
    const tipToggleHeaders = document.querySelectorAll('.tip-card-header');
    tipToggleHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const card = header.closest('.cyber-card');
            const checklist = card.querySelector('.tip-checklist');
            if (checklist) {
                // Smooth toggle effect
                if (checklist.style.display === 'none') {
                    checklist.style.display = 'block';
                    checklist.style.animation = 'slide-in 0.3s forwards';
                } else {
                    checklist.style.display = 'none';
                }
            }
        });
    });
});
