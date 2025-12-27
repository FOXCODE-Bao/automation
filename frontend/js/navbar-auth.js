const isLoggedIn = localStorage.getItem("loggedIn") === "true";
const user = JSON.parse(localStorage.getItem("user"));

const guest = document.getElementById("authGuest");
const authUser = document.getElementById("authUser");

if (isLoggedIn && user) {
  guest.style.display = "none";
  authUser.style.display = "flex";
  document.getElementById("userName").innerText = `Xin chào, ${user.name}`;
}

document.getElementById("logoutBtn")?.addEventListener("click", () => {
  localStorage.removeItem("loggedIn");
  location.reload();
});
