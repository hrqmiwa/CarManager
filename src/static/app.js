// Interações leves do CarManager: menu mobile e confirmação de exclusão.
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.querySelector(".menu-toggle");

  if (sidebar && toggle) {
    toggle.addEventListener("click", () => {
      const aberto = sidebar.classList.toggle("aberto");
      toggle.setAttribute("aria-expanded", String(aberto));
      toggle.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
    });

    document.addEventListener("click", (event) => {
      if (window.innerWidth <= 680 &&
          sidebar.classList.contains("aberto") &&
          !sidebar.contains(event.target) &&
          !toggle.contains(event.target)) {
        sidebar.classList.remove("aberto");
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 680) {
        sidebar.classList.remove("aberto");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.querySelectorAll('form[onsubmit*="confirm"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Tem certeza que deseja excluir este veículo e todos os seus registros?")) {
        event.preventDefault();
      }
    });
  });
});
