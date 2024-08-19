document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const maxSelections = parseInt(document.getElementById('max-selections').value, 10);

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const selectedCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            const continueButton = document.querySelector('button[type="submit"]');

            // Limitar el número de maletines seleccionables
            if (selectedCheckboxes.length >= maxSelections) {
                checkboxes.forEach(cb => {
                    if (!cb.checked) {
                        cb.disabled = true;
                    }
                });
            } else {
                checkboxes.forEach(cb => cb.disabled = false);
            }

            // Habilitar o deshabilitar el botón de continuar
            continueButton.disabled = selectedCheckboxes.length !== maxSelections;

            // Actualizar el estilo del maletín seleccionado
            checkboxes.forEach(checkbox => {
                const label = checkbox.parentElement;
                const numeroSpan = label.querySelector('.numero');
                if (checkbox.checked) {
                    numeroSpan.style.backgroundColor = '#FFD700'; // Fondo amarillo
                    numeroSpan.style.color = '#000'; // Color del número
                } else {
                    numeroSpan.style.backgroundColor = ''; // Sin color de fondo
                    numeroSpan.style.color = ''; // Color del número por defecto
                }
            });
        });
    });
});
