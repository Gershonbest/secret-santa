// Secret Santa App - Interactive JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Secret Santa App loaded');
    
    // Add Christmas decorations only on login/registration page
    if (document.getElementById('register-form') || document.getElementById('login-form')) {
        createSnowflakes();
        createChristmasLights();
        createGiftBoxes();
        createChristmasDecorations();
    }
    
    // Add form validation
    addFormValidation();
    
    // Add smooth scroll animations
    addScrollAnimations();
    
    // Add button ripple effects
    addRippleEffects();
});

// Create animated snowflakes for login/registration page
function createSnowflakes() {
    const snowflakeContainer = document.createElement('div');
    snowflakeContainer.className = 'snowflakes';
    document.body.appendChild(snowflakeContainer);
    
    const snowflakeSymbols = ['❄', '❅', '❆', '✻', '✼', '❉', '✦', '✧'];
    const numSnowflakes = 60;
    
    for (let i = 0; i < numSnowflakes; i++) {
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        snowflake.textContent = snowflakeSymbols[Math.floor(Math.random() * snowflakeSymbols.length)];
        snowflake.style.left = Math.random() * 100 + '%';
        snowflake.style.animationDuration = (Math.random() * 4 + 3) + 's';
        snowflake.style.animationDelay = Math.random() * 3 + 's';
        snowflake.style.fontSize = (Math.random() * 12 + 10) + 'px';
        snowflake.style.opacity = Math.random() * 0.5 + 0.3;
        snowflakeContainer.appendChild(snowflake);
    }
}

// Create Christmas lights string
function createChristmasLights() {
    const lightsContainer = document.createElement('div');
    lightsContainer.className = 'christmas-lights';
    document.body.appendChild(lightsContainer);
    
    const colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple'];
    const numLights = 20;
    const spacing = 100 / numLights;
    
    for (let i = 0; i < numLights; i++) {
        const light = document.createElement('div');
        light.className = 'christmas-light ' + colors[Math.floor(Math.random() * colors.length)];
        light.style.left = (i * spacing) + '%';
        light.style.top = '20px';
        light.style.animationDelay = (i * 0.1) + 's';
        lightsContainer.appendChild(light);
    }
}

// Create gift boxes decoration
function createGiftBoxes() {
    const positions = [
        { left: '5%', top: '15%', delay: '0s' },
        { left: '90%', top: '20%', delay: '1s' },
        { left: '8%', top: '70%', delay: '2s' },
        { left: '85%', top: '75%', delay: '1.5s' },
        { left: '12%', top: '45%', delay: '0.5s' },
        { left: '88%', top: '50%', delay: '2.5s' }
    ];
    
    positions.forEach((pos, index) => {
        const box = document.createElement('div');
        box.className = 'gift-box';
        box.style.left = pos.left;
        box.style.top = pos.top;
        box.style.animationDelay = pos.delay;
        box.style.fontSize = (Math.random() * 1.5 + 1.5) + 'rem';
        document.body.appendChild(box);
    });
}

// Create additional Christmas decorations
function createChristmasDecorations() {
    // Add some ornaments
    const ornamentPositions = [
        { left: '3%', top: '30%' },
        { left: '95%', top: '35%' },
        { left: '2%', top: '60%' },
        { left: '96%', top: '65%' }
    ];
    
    ornamentPositions.forEach(pos => {
        const ornament = document.createElement('div');
        ornament.className = 'christmas-decoration ornament';
        ornament.textContent = '🎄';
        ornament.style.left = pos.left;
        ornament.style.top = pos.top;
        ornament.style.animationDelay = Math.random() * 2 + 's';
        document.body.appendChild(ornament);
    });
    
    // Add some stars
    const starPositions = [
        { left: '10%', top: '10%' },
        { left: '90%', top: '12%' },
        { left: '15%', top: '85%' },
        { left: '92%', top: '88%' }
    ];
    
    starPositions.forEach(pos => {
        const star = document.createElement('div');
        star.className = 'christmas-decoration star';
        star.textContent = '⭐';
        star.style.left = pos.left;
        star.style.top = pos.top;
        star.style.animationDelay = Math.random() * 2 + 's';
        document.body.appendChild(star);
    });
}

// Add form validation
function addFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });
}

// Add scroll animations
function addScrollAnimations() {
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
    
    const animatedElements = document.querySelectorAll('.glow-card, .christmas-card-red, .christmas-card-green, .christmas-card-gold');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Add ripple effect to buttons
function addRippleEffects() {
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    button {
        position: relative;
        overflow: hidden;
    }
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
