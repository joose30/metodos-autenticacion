document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('phone');
    const smsForm = document.getElementById('smsForm');
    const messageDiv = document.getElementById('message');

    // Verificar que los elementos existen
    if (!smsForm) {
        console.error('❌ No se encontró el formulario con id "smsForm"');
        return;
    }

    if (!phoneInput) {
        console.error('❌ No se encontró el input con id "phone"');
        return;
    }

    if (!messageDiv) {
        console.error('❌ No se encontró el div con id "message"');
        return;
    }

    console.log('✅ Elementos del formulario cargados correctamente');

    // Escuchar el evento submit del formulario
    smsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const phoneNumber = phoneInput.value.trim();
        
        if (!phoneNumber) {
            showMessage('Por favor ingresa un número de teléfono', 'error');
            return;
        }

        try {
            console.log('📤 Enviando solicitud de SMS-LOGIN para:', phoneNumber);
            
            const response = await fetch('http://127.0.0.1:8000/sms-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ phone_number: phoneNumber })
            });

            console.log('📨 Respuesta recibida, status:', response.status);
            const data = await response.json();
            console.log('📦 Datos de respuesta:', data);

            if (response.ok && data.success) {
                // ✅ CORREGIDO: Verificar que realmente se guarda el email
                if (data.email) {
                    localStorage.setItem('pending_verification_email', data.email);
                    console.log('✅ Email guardado en localStorage:', data.email);
                    console.log('📋 Verificando localStorage:', localStorage.getItem('pending_verification_email'));
                } else {
                    console.error('❌ No se recibió email en la respuesta');
                    showMessage('Error: No se recibió información del usuario', 'error');
                    return;
                }
                
                showMessage('✅ Código enviado correctamente', 'success');
                
                // Redirigir a la página de verificación
                setTimeout(() => {
                    console.log('🔄 Redirigiendo a verificación...');
                    window.location.href = './verification/verification.html';
                }, 1500);
            } else {
                showMessage(data.error || '❌ Error al enviar el código', 'error');
            }
        } catch (error) {
            console.error('❌ Error de conexión:', error);
            showMessage('❌ Error de conexión con el servidor', 'error');
        }
    });

    function showMessage(text, type) {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} mt-3`;
        }
        console.log(`💬 [${type}] ${text}`);
    } 
});