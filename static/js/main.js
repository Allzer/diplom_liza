document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.main-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const open = nav.classList.toggle('is-open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    document.querySelectorAll('.js-phone-mask').forEach((input) => {
        input.addEventListener('input', () => formatPhone(input));
        input.addEventListener('focus', () => {
            if (!input.value) input.value = '+7 (';
        });
        if (input.value) formatPhone(input);
    });

    document.querySelectorAll('input[type="date"][name="birth_date"]').forEach((input) => {
        const today = new Date().toISOString().slice(0, 10);
        input.setAttribute('max', today);
    });

    document.querySelectorAll('.field-error').forEach((el) => {
        const label = el.closest('label');
        const field = label?.querySelector('input, textarea, select');
        if (field) field.classList.add('input-invalid');
    });
});

function formatPhone(input) {
    let digits = input.value.replace(/\D/g, '');
    if (digits.startsWith('8')) digits = '7' + digits.slice(1);
    if (!digits.startsWith('7')) digits = '7' + digits.replace(/^7/, '');
    digits = digits.slice(0, 11);

    let formatted = '+7';
    if (digits.length > 1) {
        formatted += ' (' + digits.slice(1, 4);
    }
    if (digits.length >= 4) {
        formatted += ') ' + digits.slice(4, 7);
    }
    if (digits.length >= 7) {
        formatted += '-' + digits.slice(7, 9);
    }
    if (digits.length >= 9) {
        formatted += '-' + digits.slice(9, 11);
    }

    input.value = formatted.slice(0, 18);
}

function compactPhone(value) {
    const digits = value.replace(/\D/g, '');
    let d = digits;
    if (d.startsWith('8') && d.length === 11) d = '7' + d.slice(1);
    if (d.startsWith('7') && d.length === 11) return `+${d}`;
    return value.trim();
}

document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
        form.querySelectorAll('.js-phone-mask').forEach((input) => {
            if (input.value) input.value = compactPhone(input.value);
        });
    });
});
