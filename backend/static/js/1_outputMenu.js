// Tabbed Menu Handler
function openMenu(evt, menuName) {
  var i, x, tablinks;
  x = document.getElementsByClassName("menu");

  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablink");

  for (i = 0; i < x.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" w3-dark-grey", "");
  }

  var targetEl = document.getElementById(menuName);
  if (targetEl) {
    targetEl.style.display = "block";
  }
  if (evt && evt.currentTarget && evt.currentTarget.firstElementChild) {
    evt.currentTarget.firstElementChild.className += " w3-dark-grey";
  }
}

// Safely click myLink only if it exists in the DOM
document.addEventListener("DOMContentLoaded", function () {
  var myLink = document.getElementById("myLink");
  if (myLink) {
    myLink.click();
  }
});
