/* Login y registro: mostrar contraseña y validaciones del navegador */
document.querySelectorAll("[data-toggle]").forEach((b) => {
  b.addEventListener("click", () => {
    const campo = document.getElementById(b.dataset.toggle);
    const mostrar = campo.type === "password";
    campo.type = mostrar ? "text" : "password";
    b.textContent = mostrar ? "Ocultar" : "Mostrar";
    b.setAttribute("aria-label", mostrar ? "Ocultar contraseña" : "Mostrar contraseña");
  });
});

const nombre = document.getElementById("nombre");
if (nombre) {
  nombre.addEventListener("input", () => {
    nombre.value = nombre.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]/g, "");
  });
}

const pass = document.getElementById("password");
const conf = document.getElementById("confirmar");
if (pass && conf) {
  const validar = () => conf.setCustomValidity(pass.value !== conf.value ? "Las contraseñas no coinciden." : "");
  pass.addEventListener("input", validar);
  conf.addEventListener("input", validar);
}
