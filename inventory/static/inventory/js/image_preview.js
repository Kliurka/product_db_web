document.addEventListener("click", function (event) {
    const img = event.target.closest(".preview-clickable");

    if (img) {
        const modal = document.getElementById("imageModal");
        const modalImage = document.getElementById("modalImage");

        if (modal && modalImage) {
            modalImage.src = img.src;
            modalImage.alt = img.alt || "";
            modal.style.display = "flex";
        }
    }

    if (
        event.target.id === "imageModal" ||
        event.target.classList.contains("image-close")
    ) {
        const modal = document.getElementById("imageModal");
        if (modal) {
            modal.style.display = "none";
        }
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        const modal = document.getElementById("imageModal");
        if (modal) {
            modal.style.display = "none";
        }
    }
});