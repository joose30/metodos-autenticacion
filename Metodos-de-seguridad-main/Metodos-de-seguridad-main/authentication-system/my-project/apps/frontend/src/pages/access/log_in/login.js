document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Login page loaded');
    
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            togglePassword.querySelector('i').classList.toggle('bi-eye');
            togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            console.log('📝 Form submitted');

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            if (!email || !password) {
                showMessage('Por favor completa todos los campos', 'error');
                return;
            }

            showMessage('Iniciando sesión...', 'info');

            try {
                console.log('📤 Sending login request...');
                
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({ email, password })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok && data.success) {
                    if (data.requires_otp) {
                        // Guardar email para la verificación
                        localStorage.setItem('pending_verification_email', email);
                        
                        showMessage('Redirigiendo a verificación...', 'success');
                        
                        setTimeout(() => {
                            if (data.auth_method === 'sms') {
                                // ✅ NUEVO: Para SMS, usar nuestro servicio SMS OTP
                                handleSmsLogin(email).then(() => {
                                    window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                                });
                            } else {
                                // Para TOTP, redirigir normalmente al servicio TOTP
                                window.location.href = "../../auth-methods/totp/verification/verification.html";
                            }
                        }, 1000);
                    } else {
                        // Login directo sin OTP
                        window.location.href = "../../index/index.html";
                    }
                } else {
                    showMessage(data.error || "Error al iniciar sesión", 'error');
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage("Error de conexión con el servidor", 'error');
            }
        });
    }

    // ✅ NUEVA FUNCIÓN: Manejar login SMS
    async function handleSmsLogin(email) {
        try {
            console.log('📱 Iniciando proceso SMS para:', email);
            
            // 1. Obtener información del usuario desde MongoDB (servicio SMS)
            const userResponse = await fetch('http://127.0.0.1:8000/get-user-by-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });

            if (userResponse.ok) {
                const userData = await userResponse.json();
                const phoneNumber = userData.phone_number;
                
                console.log('📞 Teléfono obtenido:', phoneNumber);
                
                if (!phoneNumber) {
                    console.error('❌ No hay número de teléfono para este usuario');
                    return;
                }

                // 2. Crear sesión y generar OTP en servicio SMS
                const smsResponse = await fetch('http://127.0.0.1:8000/create-sms-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        email: email,
                        phone_number: phoneNumber
                    })
                });

                if (smsResponse.ok) {
                    console.log('✅ Sesión SMS creada y OTP generado');
                } else {
                    console.log('⚠️ No se pudo crear sesión SMS, pero continuamos...');
                }
            } else {
                console.error('❌ Error obteniendo datos del usuario');
            }
        } catch (error) {
            console.error('❌ Error en handleSmsLogin:', error);
            // No bloqueamos el flujo si falla
        }
    }

    function showMessage(message, type) {
        if (loginMessage) {
            loginMessage.textContent = message;
            loginMessage.className = `mt-3 text-center text-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'}`;
        }
        console.log(`💬 [${type}] ${message}`);
    }
});