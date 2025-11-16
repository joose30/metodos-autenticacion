async function cerrarSesion() {
    try {
        const authMethod = localStorage.getItem('auth_method');
        
        if (authMethod === 'sms') {
            // Limpiar el almacenamiento local para SMS
            localStorage.removeItem('auth_method');
            localStorage.removeItem('isAuthenticated');
        } else {
            // Cerrar sesión TOTP
            await fetch('http://127.0.0.1:5000/logout', {
                method: 'POST',
                credentials: 'include'
            });
        }
    } catch (e) {
        console.error('Logout failed', e);
    }
    window.location.replace('../access/log_in/login.html');
}

async function cargarUsuario() {
    try {
        const authMethod = localStorage.getItem('auth_method');
        const isAuthenticated = localStorage.getItem('isAuthenticated');

        console.log('Auth Method:', authMethod);
        console.log('Is Authenticated:', isAuthenticated);

        if (!isAuthenticated) {
            console.log('No está autenticado, redirigiendo a login...');
            window.location.replace('../access/log_in/login.html');
            return;
        }

        let userData;
        let error = false;

        if (authMethod === 'sms') {
            console.log('Intentando obtener información de usuario SMS...');
            try {
                const resp = await fetch('http://127.0.0.1:8000/user-info-sms', {
                    credentials: 'include'
                });
                if (resp.ok) {
                    userData = await resp.json();
                    console.log('Datos de usuario SMS:', userData);
                } else {
                    console.error('Error al obtener datos de usuario SMS');
                    error = true;
                }
            } catch (e) {
                console.error('Error en fetch SMS:', e);
                error = true;
            }
        } else if (authMethod === 'totp') {
            console.log('Intentando obtener información de usuario TOTP...');
            try {
                const resp = await fetch('http://127.0.0.1:5000/user-info', {
                    credentials: 'include'
                });
                if (resp.ok) {
                    userData = await resp.json();
                    console.log('Datos de usuario TOTP:', userData);
                } else {
                    console.error('Error al obtener datos de usuario TOTP');
                    error = true;
                }
            } catch (e) {
                console.error('Error en fetch TOTP:', e);
                error = true;
            }
        }

        if (userData && !error) {
            console.log('Actualizando mensaje de bienvenida...');
            document.getElementById('welcome-text').textContent =
                `¡Bienvenido ${userData.first_name || 'Usuario'}!`;
        } else {
            console.error('No se pudo cargar la información del usuario');
            localStorage.clear();
            window.location.replace('../access/log_in/login.html');
        }
    } catch (error) {
        console.error('Error general:', error);
        localStorage.clear();
        window.location.replace('../access/log_in/login.html');
    }
}
cargarUsuario();