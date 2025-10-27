
        // Mobile menu functionality
        function toggleMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            if (mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            } else {
                mobileMenu.classList.add('active');
                toggle.innerHTML = '✕';
                document.body.style.overflow = 'hidden';
            }
        }

        function closeMobileMenu() {
            const mobileMenu = document.getElementById('mobileMenu');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            mobileMenu.classList.remove('active');
            toggle.innerHTML = '☰';
            document.body.style.overflow = '';
        }

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            const mobileMenu = document.getElementById('mobileMenu');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            if (!mobileMenu.contains(e.target) && !toggle.contains(e.target) && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        });

        // Demo tabs functionality
        function showDemo(type) {
            // Update active tab
            document.querySelectorAll('.demo-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');

            // Update demo content
            const content = document.getElementById('demo-content');
            
            switch(type) {
                case 'menu':
                    content.innerHTML = `
                        <h3>🍕 Піца "Маргарита"</h3>
                        <p>Соус томатний, сир моцарела, базилік свіжий</p>
                        <strong>₴280</strong>
                        <br><br>
                        <small>Приклад відображення страви в онлайн меню</small>
                    `;
                    break;
                case 'shop':
                    content.innerHTML = `
                        <h3>👕 Футболка класична</h3>
                        <p>100% бавовна, різні кольори та розміри</p>
                        <strong>₴450</strong>
                        <button style="background: #000000; color: white; padding: 8px 16px; border: none; border-radius: 6px; margin-top: 10px;">Додати в кошик</button>
                        <br><br>
                        <small>Приклад товару в інтернет-магазині</small>
                    `;
                    break;
                case 'booking':
                    content.innerHTML = `
                        <h3>💇‍♀️ Стрижка + укладання</h3>
                        <p>Тривалість: 1 година 30 хвилин</p>
                        <strong>₴800</strong>
                        <button style="background: #000000; color: white; padding: 8px 16px; border: none; border-radius: 6px; margin-top: 10px;">Записатися</button>
                        <br><br>
                        <small>Приклад послуги для онлайн запису</small>
                    `;
                    break;
            }
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    closeMobileMenu(); // Close mobile menu if open
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add scroll effect to navbar
        window.addEventListener('scroll', function() {
            const nav = document.querySelector('nav');
            if (window.scrollY > 50) {
                nav.style.background = 'rgba(255, 255, 255, 0.98)';
                nav.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                nav.style.background = 'rgba(255, 255, 255, 0.95)';
                nav.style.boxShadow = 'none';
            }
        });

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                closeMobileMenu();
            }
        });

        // Touch gesture support for mobile
        let touchStartX = 0;
        let touchStartY = 0;

        document.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchmove', function(e) {
            if (!touchStartX || !touchStartY) {
                return;
            }

            const touchEndX = e.touches[0].clientX;
            const touchEndY = e.touches[0].clientY;
            const diffX = touchStartX - touchEndX;
            const diffY = touchStartY - touchEndY;

            // If horizontal swipe is greater than vertical and mobile menu is open
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                const mobileMenu = document.getElementById('mobileMenu');
                if (mobileMenu.classList.contains('active') && diffX < 0) {
                    // Swipe right to close menu
                    closeMobileMenu();
                }
            }

            touchStartX = 0;
            touchStartY = 0;
        }, { passive: true });

        // Prevent body scroll when mobile menu is open
        document.addEventListener('touchmove', function(e) {
            const mobileMenu = document.getElementById('mobileMenu');
            if (mobileMenu.classList.contains('active')) {
                e.preventDefault();
            }
        }, { passive: false });

        // Initialize intersection observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe feature cards for animation
        document.addEventListener('DOMContentLoaded', function() {
            const featureCards = document.querySelectorAll('.feature-card');
            featureCards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                observer.observe(card);
            });
        });

        // Add keyboard navigation support
        document.addEventListener('keydown', function(e) {
            const mobileMenu = document.getElementById('mobileMenu');
            
            // Escape key closes mobile menu
            if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            }
            
            // Enter key on mobile menu toggle
            if (e.key === 'Enter' && e.target.classList.contains('mobile-menu-toggle')) {
                toggleMobileMenu();
            }
        });

        // Improve focus management for accessibility
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

        function trapFocus(element) {
            const focusableContent = element.querySelectorAll(focusableElements);
            const firstFocusableElement = focusableContent[0];
            const lastFocusableElement = focusableContent[focusableContent.length - 1];

            document.addEventListener('keydown', function(e) {
                const isTabPressed = e.key === 'Tab' || e.keyCode === 9;

                if (!isTabPressed) {
                    return;
                }

                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableElement) {
                        lastFocusableElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusableElement) {
                        firstFocusableElement.focus();
                        e.preventDefault();
                    }
                }
            });
        }

        // Apply focus trap when mobile menu is open
        document.querySelector('.mobile-menu-toggle').addEventListener('click', function() {
            const mobileMenu = document.getElementById('mobileMenu');
            if (mobileMenu.classList.contains('active')) {
                trapFocus(mobileMenu);
            }
        });
