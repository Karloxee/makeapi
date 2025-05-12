document.addEventListener('DOMContentLoaded', () => {
    fetch('/question3/data/')
      .then(r => r.json())
      .then(json => {
        new Chart(
          document.getElementById('chart3'),
          {
            type: 'pie',
            data: {
              labels: json.labels,
              datasets: [{ data: json.data }]
            }
          }
        );
      });
  });
  