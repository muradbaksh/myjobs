function showToast(message, type = "success") {

    const container =
        document.getElementById(
            "toast-container"
        );

    const toast =
        document.createElement("div");

    toast.className =
        `toast toast-${type}`;

    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}