document.addEventListener('DOMContentLoaded', () => {
    // GSAP Animations
    const tl = gsap.timeline();

    // Hero Section Animation
    tl.from("header", {
        y: -50,
        opacity: 0,
        duration: 1,
        ease: "power3.out"
    })
    .from(".text-5xl", { // Targeting the main hero title
        y: 50,
        opacity: 0,
        duration: 1,
        ease: "power3.out"
    }, "-=0.5")
    .from(".text-lg", { // Targeting the hero subtitle
        y: 50,
        opacity: 0,
        duration: 1,
        ease: "power3.out"
    }, "-=0.7")
    .from("a.bg-gradient-to-r", { // Targeting the main CTA button
        opacity: 0,
        scale: 0.8,
        duration: 0.8,
        ease: "back.out(1.7)"
    }, "-=0.5");

    // Feature cards animation on scroll
    gsap.from(".hover\\:border-blue-500", { // A bit generic, might need refinement
        scrollTrigger: {
            trigger: "#features",
            start: "top 80%",
        },
        y: 50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: "power3.out"
    });

    // Pricing cards animation on scroll
    gsap.from(".max-w-sm", {
        scrollTrigger: {
            trigger: "#pricing",
            start: "top 80%",
        },
        y: 50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: "power3.out"
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Razorpay Payment Integration
function startPayment(plan) {
    let amount;
    if (plan === 'pro') {
        amount = 99900; // ₹999 in paise
    } else if (plan === 'elite') {
        amount = 249900; // ₹2499 in paise
    } else {
        console.error("Invalid plan selected");
        return;
    }

    var options = {
        "key": "YOUR_KEY_ID", // Enter the Key ID generated from the Dashboard
        "amount": amount,
        "currency": "INR",
        "name": "EliteFnO",
        "description": `Test Transaction for ${plan} plan`,
        "image": "https://example.com/your_logo.png", // Add your logo URL
        "handler": function (response){
            alert(`Payment successful! Payment ID: ${response.razorpay_payment_id}`);
            // Here you would typically send the payment ID to your server
            // to confirm the payment and activate the user's subscription.
        },
        "prefill": {
            "name": "Test User",
            "email": "test.user@example.com",
            "contact": "9999999999"
        },
        "notes": {
            "address": "Razorpay Corporate Office"
        },
        "theme": {
            "color": "#3399cc"
        }
    };
    var rzp1 = new Razorpay(options);
    rzp1.on('payment.failed', function (response){
        alert(`Payment failed! Error code: ${response.error.code}. Description: ${response.error.description}`);
    });
    rzp1.open();
}

// Particle Animation JavaScript
class Particle {
    constructor(x, y, directionX, directionY, size, color) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.color = color;
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = this.color;
        ctx.fill();
    }
    update() {
        if (this.x > canvas.width || this.x < 0) {
            this.directionX = -this.directionX;
        }
        if (this.y > canvas.height || this.y < 0) {
            this.directionY = -this.directionY;
        }
        this.x += this.directionX;
        this.y += this.directionY;
        this.draw();
    }
}

function init() {
    particlesArray = [];
    let numberOfParticles = (canvas.height * canvas.width) / 9000;
    for (let i = 0; i < numberOfParticles; i++) {
        let size = (Math.random() * 5) + 1;
        let x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
        let y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
        let directionX = (Math.random() * 5) - 2.5;
        let directionY = (Math.random() * 5) - 2.5;
        let color = 'rgba(51, 153, 204, 0.5)';
        particlesArray.push(new Particle(x, y, directionX, directionY, size, color));
    }
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
    }
    connect();
}

function connect() {
    let opacityValue = 1;
    for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
            let distance = ((particlesArray[a].x - particlesArray[b].x) * (particlesArray[a].x - particlesArray[b].x))
                + ((particlesArray[a].y - particlesArray[b].y) * (particlesArray[a].y - particlesArray[b].y));
            if (distance < (canvas.width / 7) * (canvas.height / 7)) {
                opacityValue = 1 - (distance / 20000);
                ctx.strokeStyle = 'rgba(51, 153, 204,' + opacityValue + ')';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                ctx.stroke();
            }
        }
    }
}

const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
let particlesArray;

init();
animate();

window.addEventListener('resize', () => {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
    init();
});
