document.addEventListener("DOMContentLoaded", () => {
    const registerBtn = document.getElementById("register");
    const loginBtn = document.getElementById("login");
    const container = document.getElementById("container");

    if (registerBtn && loginBtn && container) {
        // On Sign Up button click
        registerBtn.addEventListener("click", () => {
            container.classList.add("right-panel-active");
        });

        // On Sign In button click
        loginBtn.addEventListener("click", () => {
            container.classList.remove("right-panel-active");
        });
    }

    // Toggle sections
    function showSection(sectionId) {
        const sections = document.querySelectorAll('.section');
        sections.forEach(sec => sec.style.display = 'none');
        document.getElementById(sectionId).style.display = 'block';
    }
    
    // Toggle menu
    function toggleMenu() {
        const menu = document.getElementById('menu');
        menu.classList.toggle('show');
    }
});
function toggleMenu() {
    const menu = document.getElementById('menu');
    menu.classList.toggle('show');
}
window.onload = function () {
    showSection('home');
};
