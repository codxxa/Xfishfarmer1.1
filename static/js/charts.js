document.addEventListener('DOMContentLoaded', function() {
    // Feed consumption by pond chart
    const feedCtx = document.getElementById('feedByPondChart');
    if (feedCtx) {
        const feedData = JSON.parse(feedCtx.getAttribute('data-chart'));
        
        new Chart(feedCtx, {
            type: 'bar',
            data: {
                labels: feedData.map(item => item[0]),  // Pond names
                datasets: [{
                    label: 'Feed Consumption (kg)',
                    data: feedData.map(item => item[1]),  // Feed amounts
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Feed (kg)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Pond'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Feed Consumption by Pond'
                    }
                }
            }
        });
    }

    // Mortality by cause chart
    const mortalityCtx = document.getElementById('mortalityByCauseChart');
    if (mortalityCtx) {
        const mortalityData = JSON.parse(mortalityCtx.getAttribute('data-chart'));
        
        new Chart(mortalityCtx, {
            type: 'pie',
            data: {
                labels: mortalityData.map(item => item[0]),  // Causes
                datasets: [{
                    data: mortalityData.map(item => item[1]),  // Quantities
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Mortality by Cause'
                    }
                }
            }
        });
    }

    // Financial summary chart
    const financialCtx = document.getElementById('financialSummaryChart');
    if (financialCtx) {
        const financialData = JSON.parse(financialCtx.getAttribute('data-chart'));
        
        new Chart(financialCtx, {
            type: 'line',
            data: {
                labels: financialData.labels,  // Date labels
                datasets: [
                    {
                        label: 'Income',
                        data: financialData.income,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Expenses',
                        data: financialData.expenses,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount ($)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Financial Summary'
                    }
                }
            }
        });
    }

    // Stock levels chart
    const stockCtx = document.getElementById('stockLevelsChart');
    if (stockCtx) {
        const stockData = JSON.parse(stockCtx.getAttribute('data-chart'));
        
        new Chart(stockCtx, {
            type: 'doughnut',
            data: {
                labels: stockData.labels,  // Species labels
                datasets: [{
                    data: stockData.data,  // Stock quantities
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Current Stock Levels by Species'
                    }
                }
            }
        });
    }
});
