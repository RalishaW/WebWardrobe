document.addEventListener("DOMContentLoaded", () => {
  if (window.location.hostname !== 'test') {
    const flashes = document.querySelector(".flashes");
    if (flashes) {
      setTimeout(() => {
        flashes.style.display = "none"; // Auto-hide flash messages after 8 seconds
      }, 8000);
    }
  }

  if (
    document.getElementById("category-chart") ||
    document.getElementById("season-chart") ||
    document.getElementById("color-chart")
  ) {
    requestAnimationFrame(() => {
      setTimeout(() => fetchDataAndRenderCharts(), 0);
    });
  }
});

function fixCanvasResolution(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
}

async function fetchDataAndRenderCharts() {
  const response = await fetch("/analysis/data");
  const data = await response.json();

  const fallbackData = {
    labels: ["No data"],
    datasets: [
      {
        data: [1],
        backgroundColor: ["#e0e0e0"]
      }
    ]
  };

  const fallbackOptions = (title) => ({
    responsive: true,
    maintainAspectRatio: true,
    animation: {
      duration: 1000,
      easing: "easeOutQuart"
    },
    plugins: {
      title: {
        display: true,
        text: title,
        font: {
          size: 18,
          weight: "bold"
        },
        padding: {
          top: 10,
          bottom: 20
        }
      },
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 20,
          font: {
            size: 12
          },
          padding: 15
        }
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label || ""}: ${context.parsed} items`;
          }
        }
      }
    }
  });

  function renderChart(id, configFn) {
    const oldCanvas = document.getElementById(`${id}-chart`);
    const newCanvas = oldCanvas.cloneNode(true);
    oldCanvas.parentNode.replaceChild(newCanvas, oldCanvas);
    fixCanvasResolution(newCanvas);
    new Chart(newCanvas, configFn());
  }

  renderChart("category", () => ({
    type: "doughnut",
    data: Object.keys(data.category_counts).length
      ? {
          labels: Object.keys(data.category_counts),
          datasets: [
            {
              data: Object.values(data.category_counts),
              backgroundColor: [
                "#4F81BD",
                "#A6A6A6",
                "#F79646",
                "#9BBB59",
                "#8064A2"
              ]
            }
          ]
        }
      : fallbackData,
    options: fallbackOptions("Wardrobe by Category")
  }));

  renderChart("season", () => ({
    type: "doughnut",
    data: Object.keys(data.season_counts).length
      ? {
          labels: Object.keys(data.season_counts),
          datasets: [
            {
              data: Object.values(data.season_counts),
              backgroundColor: [
                "#92D050",
                "#FFD966",
                "#F4B183",
                "#9DC3E6"
              ]
            }
          ]
        }
      : fallbackData,
    options: {
      rotation: -90,
      circumference: 180,
      ...fallbackOptions("Wardrobe by Season")
    }
  }));

  renderChart("color", () => ({
    type: "bar",
    data: Object.keys(data.color_counts).length
      ? {
          labels: Object.keys(data.color_counts),
          datasets: [
            {
              data: Object.values(data.color_counts),
              backgroundColor: Object.keys(data.color_counts).map((color) =>
                color.toLowerCase()
              ),
              borderColor: "#ccc",
              borderWidth: 1
            }
          ]
        }
      : {
          labels: ["No data"],
          datasets: [
            {
              data: [0],
              backgroundColor: ["#e0e0e0"],
              borderColor: "#ccc",
              borderWidth: 1
            }
          ]
        },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      animation: {
        duration: 1000,
        easing: "easeOutQuart"
      },
      plugins: {
        title: {
          display: true,
          text: "Wardrobe by Color",
          font: {
            size: 18,
            weight: "bold"
          },
          padding: {
            top: 10,
            bottom: 20
          }
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
            text: "Colors",
            font: {
              size: 14,
              weight: "bold"
            }
          },
          ticks: {
            font: {
              size: 12
            }
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            callback: function (value) {
              return Number.isInteger(value) ? value : null;
            },
            font: {
              size: 12
            }
          },
          title: {
            display: true,
            text: "Number of Items",
            font: {
              size: 14,
              weight: "bold"
            }
          }
        }
      }
    }
  }));
}
