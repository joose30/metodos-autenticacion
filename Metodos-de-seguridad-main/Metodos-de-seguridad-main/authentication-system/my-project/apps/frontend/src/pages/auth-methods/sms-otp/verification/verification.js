document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Verification page loaded');
    
    const otpInput = document.getElementById('otp');
    const verifyButton = document.getElementById('verifyOTP');
    const resendButton = document.getElementById('resendOTP');
    const messageDiv = document.getElementById('message');

    // Auto-focus en el input
    if (otpInput) {
        otpInput.focus();
    }

    // Verificar OTP
    if (verifyButton) {
        verifyButton.addEventListener('click', async () => {
            console.log('🔍 Verify button clicked');
            
            const otp = otpInput.value.trim();
            
            if (!otp || otp.length !== 6) {
                showMessage('Por favor ingresa un código válido de 6 dígitos', 'error');
                return;
            }

            verifyButton.disabled = true;
            verifyButton.textContent = 'Verificando...';

            try {
                console.log('📤 Sending verification request to port 8000...');
                
                // ✅ CAMBIO: Obtener email del localStorage y enviarlo explícitamente
                const email = localStorage.getItem('pending_verification_email');
                console.log('📧 Email enviado en verificación:', email);
                
                const response = await fetch('http://127.0.0.1:8000/verify-otp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        otp: otp,
                        email: email // ✅ ENVIAR EMAIL EXPLÍCITAMENTE
                    })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok && data.valid) {
                    showMessage('✅ Verificación exitosa. Redirigiendo al dashboard...', 'success');
                    
                    // Limpiar datos temporales
                    localStorage.removeItem('pending_verification_email');
                    
                    // Establecer la sesión antes de redirigir
                    localStorage.setItem('auth_method', 'sms');
                    localStorage.setItem('isAuthenticated', 'true');
                    localStorage.setItem('user_email', data.email || email || '');
                    
                    // REDIRECCIÓN CORREGIDA - Ruta absoluta al dashboard real
                    setTimeout(() => {
                        window.location.href = '/authentication-system/my-project/apps/frontend/src/pages/index/index.html';
                    }, 1500);
                } else {
                    showMessage(data.error || '❌ Código inválido', 'error');
                    otpInput.value = '';
                    otpInput.focus();
                    
                    verifyButton.disabled = false;
                    verifyButton.textContent = 'Verificar';
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión', 'error');
                
                verifyButton.disabled = false;
                verifyButton.textContent = 'Verificar';
            }
        });
    }

    // Reenviar OTP (ESTE SÍ FUNCIONA)
    if (resendButton) {
        resendButton.addEventListener('click', async () => {
            console.log('🔄 Resend button clicked');
            
            resendButton.disabled = true;
            resendButton.textContent = 'Enviando...';

            try {
                console.log('📤 Sending resend request to port 8000...');
                
                // Obtener el email del localStorage
                const email = localStorage.getItem('pending_verification_email');
                console.log('📧 Email from localStorage:', email);
                
                if (!email) {
                    showMessage('❌ No se encontró información de verificación', 'error');
                    resendButton.disabled = false;
                    resendButton.textContent = 'Reenviar código';
                    return;
                }

                const response = await fetch('http://127.0.0.1:8000/resend-otp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        email: email
                    })
                });

                const data = await response.json();
                console.log('📦 Response:', data);

                if (response.ok) {
                    showMessage('✅ Nuevo código enviado', 'success');
                    otpInput.value = '';
                    otpInput.focus();
                } else {
                    showMessage(data.error || '❌ Error al reenviar el código', 'error');
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión', 'error');
            } finally {
                resendButton.disabled = false;
                resendButton.textContent = 'Reenviar código';
            }
        });
    }

    // Permitir Enter para verificar
    if (otpInput) {
        otpInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && verifyButton) {
                verifyButton.click();
            }
        });
    }

    function showMessage(text, type) {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = type;
        }
        console.log(`💬 [${type}] ${text}`);
    }

    // Verificar si hay email en localStorage al cargar la página
    const storedEmail = localStorage.getItem('pending_verification_email');
    if (storedEmail) {
        console.log('📧 Email encontrado en localStorage:', storedEmail);
        showMessage(`📱 Ingresa el código enviado por SMS para ${storedEmail}`, 'info');
    } else {
        console.log('⚠️ No se encontró email en localStorage');
        showMessage('⚠️ No se encontró información de verificación', 'error');
    }
});