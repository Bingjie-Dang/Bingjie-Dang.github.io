// 打字机效果配置
var typed = new Typed('#typed', {
    strings: ['Research Fellow at NUS.', 'PhD from Peking University.', 'Expert in Memristors.'],
    typeSpeed: 50,
    backSpeed: 30,
    loop: true
});

// 粒子特效配置
particlesJS('particles-js', {
    "particles": {
        "number": { "value": 80 },
        "color": { "value": "#d2b4a0" },
        "shape": { "type": "circle" },
        "opacity": { "value": 0.5 },
        "size": { "value": 3 },
        "line_linked": { "enable": true, "distance": 150, "color": "#d2b4a0", "opacity": 0.4, "width": 1 },
        "move": { "enable": true, "speed": 2 }
    }
});
