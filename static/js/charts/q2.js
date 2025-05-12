document.addEventListener('DOMContentLoaded', () => {
    fetch('/question2/data/')
      .then(r => r.json())
      .then(json => {
        new Chart(
          document.getElementById('chart2'),
          {
            type: 'bar',
            data: {
              labels: json.labels,
              datasets: json.datasets.map(ds => ({
                label: ds.label,
                data: ds.data,
                backgroundColor: `hsla(${Math.random()*360},70%,50%,0.5)`
              }))
            },
            options: { scales: { y: { beginAtZero: true } } }
          }
        );
      });
  });
  