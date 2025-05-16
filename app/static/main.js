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

function colorNameToHex(name) {
  const colorMap = {
    white: "#F5F5F5",
    black: "#2E2E2E",
    gray: "#B0B0B0",
    red: "#E74C3C",
    blue: "#3498DB",
    green: "#27AE60",
    yellow: "#F1C40F",
    purple: "#9B59B6",
    brown: "#8D6E63",
    multicolor: "#FF69B4", // Hot pink - playful
    other: "#95A5A6",       // Soft gray-blue
    default: "#CCCCCC"
  };

  return colorMap[name.toLowerCase()] || colorMap["default"];
}

function seasonNameToColor(name) {
  const seasonMap = {
    spring: "#B4E197",      // Soft green
    summer: "#FFF7AE",      // Warm yellow
    fall: "#FFBC97",        // Earthy orange
    autumn: "#FFBC97",      // (alias)
    winter: "#A0D2EB",      // Cool blue
    "all season": "#A3D5D3", // Pastel teal – upgraded!
    default: "#CCCCCC"
  };

  return seasonMap[name.toLowerCase()] || seasonMap["default"];
}

function categoryNameToColor(name) {
  const categoryMap = {
    "t-shirt": "#87CEEB",
    "shirt": "#48D1CC",
    "blouse": "#DA70D6",
    "sweater": "#808000",
    "hoodie": "#DDA0DD",
    "coat": "#000080",
    "pant": "#F0E68C",
    "jeans": "#4169E1",
    "shorts": "#FF7F50",
    "skirt": "#FA8072",
    "dress": "#E6E6FA",
    "shoes": "#8B4513",
    "jackets": "#708090",
    "accessory": "#FFD700",
    "other": "#D3D3D3",
    "default": "#CCCCCC"
  };

  return categoryMap[name.toLowerCase()] || categoryMap["default"];
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
    type: "pie",
    data: Object.keys(data.category_counts).length
      ? {
          labels: Object.keys(data.category_counts),
          datasets: [
            {
              data: Object.values(data.category_counts),
              backgroundColor: 
                Object.keys(data.category_counts).map(type =>
                  categoryNameToColor(type)
              )
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
              backgroundColor:
                Object.keys(data.season_counts).map(season =>
                seasonNameToColor(season)
              )
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
          labels: Object.keys(data.color_counts).map(label =>
            label.charAt(0).toUpperCase() + label.slice(1)
          ),
          datasets: [
            {
              data: Object.values(data.color_counts),
              backgroundColor: Object.keys(data.color_counts).map(color =>
                colorNameToHex(color)
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
              return `${context.label || ""}: ${context.parsed.y} items`;
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

// profile.html
// togglePasswordForm: view password form
function togglePasswordForm() {
  const form = document.getElementById("password-form");
  form.style.display = form.style.display === "none" ? "block" : "none";
}
// Delete account confirmation pop-up
function showDeleteModal() {
  document.getElementById("delete-modal").style.display = "block";
}

function hideDeleteModal() {
  document.getElementById("delete-modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("trigger-delete")?.addEventListener("click", showDeleteModal);
  document.getElementById("cancel-delete")?.addEventListener("click",  hideDeleteModal);
});


//wardrobe.html

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#upload-form form');
  const submitBtn = document.getElementById('submit-btn');

  form.addEventListener('submit', function () {
      submitBtn.disabled = true;
      submitBtn.value = 'Uploading...'; // Optional: change button text
  });
});

function toggleUploadForm() {
  const form = document.getElementById("upload-form");
  form.style.display = form.style.display === "none" ? "flex" : "none";
}

// Image preview on upload
function previewImage(event) {
  const preview = document.getElementById('image-preview');
  preview.src = URL.createObjectURL(event.target.files[0]);
}

const filterGroups = {
  "Tops": ["Top", "T-Shirt", "Shirt", "Blouse", "Sweater", "Hoodie"],
  "Pants": ["Pant", "Jeans", "Shorts"],
  "Jackets": ["Jackets", "Coat"],
  "Dresses": ["Dress"],
  "Shoes": ["Shoes"],
  "Accessories": ["Accessory"]
};

// Wardrobe item filter
function filterWardrobe(type, event) {
  const buttons = document.querySelectorAll('.filters[data-type="type"] .filter-btn');
  buttons.forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');

  // Normalize filter type
  const normalizedType = type.toLowerCase().trim();

  document.querySelectorAll('.wardrobe-item').forEach(item => {
      const itemType = item.getAttribute('data-type')?.toLowerCase().trim();

      if (normalizedType === 'all') {
          item.style.display = '';
          return;
      }

      let showItem = false;

      // Check if filter group exists
      Object.keys(filterGroups).forEach(groupName => {
          const groupItems = filterGroups[groupName].map(t => t.toLowerCase().trim());

          if (groupName.toLowerCase() === normalizedType && groupItems.includes(itemType)) {
              showItem = true;
          }
      });

      // If not in group, directly compare type
      if (!showItem && normalizedType === itemType) {
          showItem = true;
      }

      item.style.display = showItem ? '' : 'none';
  });
}


//Outfit.html
let selectedSeason = "all";
        let selectedOccasion = "all";

        function filterOutfits(value, filterType, event) {
            // Toggle active class
            const filterButtons = document.querySelectorAll(`.filters[data-type="${filterType}"] .filter-btn`);
            filterButtons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            // Update selected filter
            if (filterType === 'season') {
                selectedSeason = value.toLowerCase();
            } else if (filterType === 'occasion') {
                selectedOccasion = value.toLowerCase();
            }

            // Apply combined filtering
            document.querySelectorAll(".outfit-item").forEach(item => {
                const itemSeason = item.dataset.season?.toLowerCase() || '';
                const itemOccasion = item.dataset.occasion?.toLowerCase() || '';

                const matchSeason = (selectedSeason === "all" || itemSeason === selectedSeason);
                const matchOccasion = (selectedOccasion === "all" || itemOccasion === selectedOccasion);

                item.style.display = (matchSeason && matchOccasion) ? "" : "none";
            });
        }

        function openShareModal(outfitId) {
            document.getElementById('modalOutfitId').value = outfitId;
            document.getElementById('shareModal').style.display = 'flex';
        }

        function closeShareModal() {
            document.getElementById('shareModal').style.display = 'none';
        }

        function hidePreview() {
            document.getElementById('preview-container').style.display = 'none';
        }
