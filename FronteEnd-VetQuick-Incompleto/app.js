const form = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const rememberCheckbox = document.getElementById("rememberMe");
const togglePasswordBtn = document.getElementById("togglePassword");
const submitBtn = document.getElementById("submitBtn");
const alertBox = document.getElementById("alertBox");
const emailError = document.getElementById("emailError");
const passwordError = document.getElementById("passwordError");
const API_BASE_URL = (
  window.VETQUICK_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

// Restaura e-mail salvo, se existir
const savedEmail = localStorage.getItem("vetquick_email");
if (savedEmail) {
  emailInput.value = savedEmail;
  rememberCheckbox.checked = true;
}

// Mostrar / ocultar senha
togglePasswordBtn.addEventListener("click", () => {
  const isPassword = passwordInput.type === "password";
  passwordInput.type = isPassword ? "text" : "password";
  togglePasswordBtn.setAttribute("aria-pressed", String(isPassword));
  togglePasswordBtn.setAttribute("aria-label", isPassword ? "Ocultar senha" : "Mostrar senha");
});

function showAlert(type, message) {
  alertBox.className = `alert show ${type}`;
  alertBox.textContent = message;
}

function clearAlert() {
  alertBox.className = "alert";
  alertBox.textContent = "";
}

function validateEmail() {
  const value = emailInput.value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const valid = emailRegex.test(value);
  emailInput.classList.toggle("invalid", !valid);
  emailError.classList.toggle("show", !valid);
  return valid;
}

function validatePassword() {
  const valid = passwordInput.value.length >= 8;
  passwordInput.classList.toggle("invalid", !valid);
  passwordError.classList.toggle("show", !valid);
  return valid;
}

function getApiError(data, status) {
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg;
  }
  if (status === 401) return "E-mail ou senha inválidos.";
  if (status === 403) return "Acesso não liberado para este veterinário.";
  if (status === 0) return "Não foi possível conectar à API VetQuick.";
  return "Não foi possível realizar o login.";
}

emailInput.addEventListener("input", () => {
  clearAlert();
  if (emailInput.classList.contains("invalid")) validateEmail();
});

passwordInput.addEventListener("input", () => {
  clearAlert();
  if (passwordInput.classList.contains("invalid")) validatePassword();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAlert();

  const isEmailValid = validateEmail();
  const isPasswordValid = validatePassword();

  if (!isEmailValid || !isPasswordValid) {
    showAlert("error", "Verifique os campos destacados antes de continuar.");
    return;
  }

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (rememberCheckbox.checked) {
    localStorage.setItem("vetquick_email", email);
  } else {
    localStorage.removeItem("vetquick_email");
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Entrando...";

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        email,
        senha: password,
      }),
    });

    let data = null;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(getApiError(data, response.status));
    }

    if (!data?.access_token) {
      throw new Error("A API não retornou um token de acesso.");
    }

    sessionStorage.setItem("vetquick_token", data.access_token);
    sessionStorage.setItem("vetquick_token_type", data.token_type || "bearer");
    sessionStorage.setItem("vetquick_expires_in", String(data.expires_in));

    const profileResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${data.access_token}`,
      },
    });

    let profile = null;
    try {
      profile = await profileResponse.json();
    } catch {
      profile = null;
    }
    if (!profileResponse.ok) {
      throw new Error(getApiError(profile, profileResponse.status));
    }
    if (!Number.isInteger(Number(profile?.id_vets))) {
      throw new Error("O perfil retornado não contém um veterinário válido.");
    }
    sessionStorage.setItem("vetquick_veterinario_id", String(profile.id_vets));
    sessionStorage.setItem("vetquick_veterinario", JSON.stringify(profile));
    window.location.href = "dashboard.html";
  } catch (err) {
    sessionStorage.removeItem("vetquick_token");
    sessionStorage.removeItem("vetquick_token_type");
    sessionStorage.removeItem("vetquick_expires_in");
    sessionStorage.removeItem("vetquick_veterinario");
    sessionStorage.removeItem("vetquick_veterinario_id");

    if (err instanceof TypeError) {
      showAlert("error", getApiError(null, 0));
    } else {
      showAlert("error", err.message || "Não foi possível realizar o login.");
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Entrar";
  }
});

document.getElementById("forgotLink").addEventListener("click", (e) => {
  e.preventDefault();
  const currentEmail = emailInput.value.trim();
  showAlert(
    "success",
    currentEmail
      ? `Se ${currentEmail} estiver cadastrado, enviaremos instruções de recuperação.`
      : "Digite seu e-mail profissional acima para recuperar a senha."
  );
});

document.getElementById("supportLink").addEventListener("click", (e) => {
  e.preventDefault();
  showAlert("success", "Suporte VetQuick: suporte@vetquick.com.br");
});