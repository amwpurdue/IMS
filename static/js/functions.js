function createCollapsible(element) {
    let content = element.nextElementSibling;
  element.addEventListener("click", function() {
    this.classList.toggle("active");
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
document
