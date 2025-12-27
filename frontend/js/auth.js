// Register
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.onsubmit = (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(registerForm));
    localStorage.setItem("user", JSON.stringify(data));

    alert("Đăng ký thành công!");
    window.location.href = "login.html";
  };
}

// Login
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.onsubmit = (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(loginForm));
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user || user.email !== data.email || user.password !== data.password) {
      alert("Sai thông tin đăng nhập");
      return;
    }

    localStorage.setItem("loggedIn", "true");
    alert("Đăng nhập thành công!");
    window.location.href = "index.html";
  };
}
