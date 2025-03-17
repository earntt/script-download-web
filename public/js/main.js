// This is an example of an external JavaScript file
console.log("External script loaded successfully!")

// You can define functions here that will be available globally
function updateDynamicContent(content) {
  const container = document.getElementById("dynamic-content")
  if (container) {
    container.innerHTML = content
  }
}

// Initialize any functionality when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded and parsed")

  // Example of accessing and modifying the dynamic content area
  const dynamicContent = document.getElementById("dynamic-content")
  if (dynamicContent) {
    dynamicContent.innerHTML = "<p>This content was dynamically inserted by main.js</p>"
  }
})

