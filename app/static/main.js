document.addEventListener("DOMContentLoaded", () => {
  // Only hide in non-test environment
  if (window.location.hostname !== 'test') {
    const flashes = document.querySelector(".flashes"); 
    if (flashes) {
      setTimeout(() => {
        flashes.style.display = "none";  // Auto-hide flash messages after 8 seconds
      }, 8000);
    }
  }

  // Only run chart rendering if the user is on the analysis page
  if (document.getElementById('category-chart') || document.getElementById('season-chart') || document.getElementById('color-chart')) {
    fetchDataAndRenderCharts();
  }
});
async function fetchDataAndRenderCharts() {
  const response = await fetch('/analysis/data');
  const data = await response.json();

  const fallbackData = {
    labels: ['No data'],
    datasets: [{
      data: [1],
      backgroundColor: ['#e0e0e0']
    }]
  };

  const fallbackOptions = (title) => ({
    plugins: {
      title: {
        display: true,
        text: title
      }
    }
  });

  const categoryCanvas = document.getElementById('category-chart');
  if (categoryCanvas) {
    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: Object.keys(data.category_counts).length ? {
        labels: Object.keys(data.category_counts),
        datasets: [{
          data: Object.values(data.category_counts),
          backgroundColor: ['#4F81BD', '#A6A6A6', '#F79646', '#9BBB59', '#8064A2']
        }]
      } : fallbackData,
      options: fallbackOptions('Wardrobe by Category')
    });
  }

  const seasonCanvas = document.getElementById('season-chart');
  if (seasonCanvas) {
    new Chart(seasonCanvas, {
      type: 'doughnut',
      data: Object.keys(data.season_counts).length ? {
        labels: Object.keys(data.season_counts),
        datasets: [{
          data: Object.values(data.season_counts),
          backgroundColor: ['#92D050', '#FFD966', '#F4B183', '#9DC3E6']
        }]
      } : fallbackData,
      options: {
        rotation: -90,
        circumference: 180,
        ...fallbackOptions('Wardrobe by Season')
      }
    });
  }

  const colorCanvas = document.getElementById('color-chart');
  if (colorCanvas) {
    new Chart(colorCanvas, {
      type: 'bar',
      data: Object.keys(data.color_counts).length ? {
        labels: Object.keys(data.color_counts),
        datasets: [{
          data: Object.values(data.color_counts),
          backgroundColor: Object.keys(data.color_counts).map(color => color.toLowerCase()),
          borderColor: '#ccc',
          borderWidth: 1
        }]
      } : {
        labels: ['No data'],
        datasets: [{
          data: [0],
          backgroundColor: ['#e0e0e0'],
          borderColor: '#ccc',
          borderWidth: 1
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: 'Wardrobe by Color'
          },
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.parsed.y} items`;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Colors'
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              callback: function (value) {
                return Number.isInteger(value) ? value : null;
              }
            },
            title: {
              display: true,
              text: 'Number of Items'
            }
          }
        }
      }
    });
  }
}
