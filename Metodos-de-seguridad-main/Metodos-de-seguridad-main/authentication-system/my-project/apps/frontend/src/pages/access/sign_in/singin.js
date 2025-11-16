document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sign in page loaded');
    
    // Toggle password visibility
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            togglePassword.querySelector('i').classList.toggle('bi-eye');
            togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }

    if (toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('click', () => {
            const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPassword.setAttribute('type', type);
            toggleConfirmPassword.querySelector('i').classList.toggle('bi-eye');
            toggleConfirmPassword.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }
});

document.getElementById("registerBtn").addEventListener("click", async () => {
    console.log('📝 Register button clicked');
    
    const first_name = document.getElementById("first_name").value.trim();
    const email = document.getElementById("your_email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const authMethodElement = document.querySelector('input[name="authMethod"]:checked');
    const phone_number = document.getElementById("phone_number").value.trim();

    // Validaciones
    if (!email || !email.includes("@")) {
        alert("❌ Por favor ingresa un correo válido.");
        return;
    }

    if (!password || password.length < 6) {
        alert("❌ La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    if (password !== confirmPassword) {
        alert("❌ Las contraseñas no coinciden.");
        return;
    }

    if (!authMethodElement) {
        alert("❌ Por favor selecciona un método de autenticación.");
        return;
    }

    const authMethod = authMethodElement.value;

    if (authMethod === 'sms' && !phone_number) {
        alert("❌ Por favor ingresa un número de teléfono.");
        return;
    }

    try {
        console.log('📤 Sending registration request...');
        
        // DETERMINAR URL SEGÚN MÉTODO DE AUTENTICACIÓN
        const url = authMethod === 'sms' 
            ? "http://127.0.0.1:8000/register"  // SMS OTP en puerto 8000
            : "http://127.0.0.1:5000/register"; // TOTP en puerto 5000
        
        console.log(`🎯 Using URL: ${url} for auth method: ${authMethod}`);

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include", 
            body: JSON.stringify({ 
                email, 
                password, 
                first_name, 
                auth_method: authMethod,
                phone_number: phone_number 
            })
        });

        console.log('📨 Response status:', response.status);
        
        const data = await response.json();
        console.log('📦 Response data:', data);

        if (response.ok) {
            if (authMethod === 'sms') {
                // VERIFICAR SI EL OTP SE ENVIÓ CORRECTAMENTE
                if (data.success && data.requires_otp) {
                    alert("✅ Usuario registrado correctamente. Se envió un código por SMS.");
                    
                    // Guardar email para verificación
                    localStorage.setItem('pending_verification_email', email);
                    
                    // Redirigir a verificación SMS
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                    }, 1000);
                } else {
                    // AUNQUE FALLE EL ENVÍO AUTOMÁTICO, PERMITIR REENVÍO MANUAL
                    alert("⚠️ Usuario registrado. Si no recibes el SMS, usa 'Reenviar código' en la siguiente pantalla.");
                    
                    // Guardar email igualmente para permitir reenvío
                    localStorage.setItem('pending_verification_email', email);
                    
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                    }, 1000);
                }
            } else {
                // Para TOTP
                alert("✅ Usuario registrado correctamente. Escanea el QR en la app de autenticación.");
                window.location.href = "../../auth-methods/totp/qr_scan/qr.html";
            }
        } else {
            // SI HAY ERROR 500 PERO EL USUARIO SE GUARDÓ, REDIRIGIR IGUAL
            if (response.status === 500 && data.error === 'Failed to send OTP') {
                alert("⚠️ Usuario registrado. Si no recibes el SMS, usa 'Reenviar código'.");
                localStorage.setItem('pending_verification_email', email);
                setTimeout(() => {
                    window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                }, 1000);
            } else {
                alert("❌ Error: " + (data.error || 'Error en el registro'));
            }
        }
    } catch (error) {
        console.error('❌ Error:', error);
        
        // MANEJO ESPECÍFICO PARA CONEXIÓN RECHAZADA
        if (error.toString().includes('Failed to fetch') || error.toString().includes('CONNECTION_REFUSED')) {
            alert("❌ No se puede conectar al servidor. Verifica que el servicio SMS OTP esté ejecutándose en puerto 8000.");
        } else {
            alert("❌ Error al conectar con el servidor: " + error.message);
        }
    }
});