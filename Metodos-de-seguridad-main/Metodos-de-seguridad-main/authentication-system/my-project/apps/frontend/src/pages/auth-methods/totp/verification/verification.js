var value = ""
const btn_submt = document.querySelector('.submit_btn');
btn_submt.disabled = true
const inputs = Array.from(document.querySelectorAll('input[class^="form-control"]'));

inputs.forEach((input, idx) => {
    input.setAttribute('maxlength', 1);

    input.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        updateValue();
        if (e.target.value.length === 1 && idx < inputs.length - 1) {
            inputs[idx + 1].focus();
        }
        subIsActive();

    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && e.target.value === '' && idx > 0) {
            inputs[idx - 1].focus();
        }
        setTimeout(() => {
            updateValue();
            subIsActive();
        }, 0);
    });

});

function subIsActive() {
    const filled = inputs.filter(input => input.value.length === 1).length;
    btn_submt.disabled = filled !== 6;
}

function updateValue() {
    value = inputs.map(input => input.value).join('');
}


btn_submt.addEventListener('click', () => {
    const otpCode = inputs.map(input => input.value).join('');

    fetch('http://127.0.0.1:5000/validate', {
        method: 'POST',
        credentials: 'include',      
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: otpCode })
    })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Establecer la sesión antes de redirigir
                localStorage.setItem('auth_method', 'totp');
                localStorage.setItem('isAuthenticated', 'true');
                
                // Redirigir al index
                window.location.href = "/authentication-system/my-project/apps/frontend/src/pages/index/index.html";
            } else {
                alert('Código OTP inválido');
            }
        })
        .catch(error => {
            console.error('Error al validar OTP:', error);
        });
});
