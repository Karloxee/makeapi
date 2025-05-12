document.addEventListener('DOMContentLoaded', () => {
    fetch('/question1/data/')
      .then(r => r.json())
      .then(json => {
        new Chart(
          document.getElementById('chart1'),
          {
            type: 'bar',
            data: {
              labels: json.labels,
              datasets: [{
                label: 'Sanisettes',
                data: json.data,
                backgroundColor: 'rgba(54,162,235,0.5)'
              }]
            },
            options: { scales: { y: { beginAtZero: true } } }
          }
        );
      });
  });
  