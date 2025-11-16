document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("qrContainer");
    // Evitar cargar múltiples veces
    if (container.querySelector("img")) return;

    try {
        const response = await fetch("http://127.0.0.1:5000/qr", {
            method: "GET",
            credentials: "include"
        });
        document.getElementById("scannedBtn").addEventListener("click", () => {
            window.location.href = "../verification/verification.html";
        });

        if (!response.ok) {
            container.textContent = "No autorizado. Por favor inicia sesión.";
            console.error("No autorizado", response.status);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const img = document.createElement("img");
        img.src = url;
        img.alt = "QR Code";
        img.className = "img-fluid";

        container.appendChild(img);
    } catch (error) {
        container.textContent = "Error al cargar el QR. Verifica conexión con el servidor.";
        console.error(error);
    }
});