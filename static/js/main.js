document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Task completion toggle
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.getAttribute('data-task-id');
            const taskForm = document.getElementById(`complete-task-${taskId}`);
            if (this.checked) {
                taskForm.submit();
            }
        });
    });

    // Calculate total amount for sales form
    const weightInput = document.getElementById('weight');
    const pricePerKgInput = document.getElementById('price_per_kg');
    const totalAmountDisplay = document.getElementById('total-amount-display');
    
    if (weightInput && pricePerKgInput && totalAmountDisplay) {
        const calculateTotal = function() {
            const weight = parseFloat(weightInput.value) || 0;
            const pricePerKg = parseFloat(pricePerKgInput.value) || 0;
            const totalAmount = weight * pricePerKg;
            totalAmountDisplay.textContent = totalAmount.toFixed(2);
        };
        
        weightInput.addEventListener('input', calculateTotal);
        pricePerKgInput.addEventListener('input', calculateTotal);
    }

    // Calculate total amount for invoice form
    const amountInput = document.getElementById('amount');
    const taxAmountInput = document.getElementById('tax_amount');
    const invoiceTotalDisplay = document.getElementById('invoice-total-display');
    
    if (amountInput && taxAmountInput && invoiceTotalDisplay) {
        const calculateInvoiceTotal = function() {
            const amount = parseFloat(amountInput.value) || 0;
            const taxAmount = parseFloat(taxAmountInput.value) || 0;
            const totalAmount = amount + taxAmount;
            invoiceTotalDisplay.textContent = totalAmount.toFixed(2);
        };
        
        amountInput.addEventListener('input', calculateInvoiceTotal);
        taxAmountInput.addEventListener('input', calculateInvoiceTotal);
    }

    // Logo preview when file is selected
    const logoInput = document.getElementById('logo');
    const logoPreview = document.getElementById('logo-preview');
    
    if (logoInput && logoPreview) {
        logoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    logoPreview.src = e.target.result;
                    logoPreview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Task filtering
    const taskFilterSelect = document.getElementById('task-filter');
    const taskRows = document.querySelectorAll('.task-row');
    
    if (taskFilterSelect && taskRows.length > 0) {
        taskFilterSelect.addEventListener('change', function() {
            const filterValue = this.value;
            
            taskRows.forEach(row => {
                if (filterValue === 'all' || 
                    (filterValue === 'completed' && row.classList.contains('task-completed')) ||
                    (filterValue === 'pending' && !row.classList.contains('task-completed'))) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Completed vs pending task counts
    updateTaskCounts();
    
    function updateTaskCounts() {
        const totalTasks = document.querySelectorAll('.task-row').length;
        const completedTasks = document.querySelectorAll('.task-row.task-completed').length;
        const pendingTasks = totalTasks - completedTasks;
        
        const totalCountElement = document.getElementById('total-task-count');
        const completedCountElement = document.getElementById('completed-task-count');
        const pendingCountElement = document.getElementById('pending-task-count');
        
        if (totalCountElement) totalCountElement.textContent = totalTasks;
        if (completedCountElement) completedCountElement.textContent = completedTasks;
        if (pendingCountElement) pendingCountElement.textContent = pendingTasks;
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
});
