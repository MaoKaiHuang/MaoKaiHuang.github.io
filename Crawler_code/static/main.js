let chartInstance = null;

document.getElementById('searchForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  const response = await fetch('/search', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  const resultDiv = document.getElementById('result');
  const chartCanvas = document.getElementById('ratingChart');

  if (data.error) {
    resultDiv.innerHTML = `<p>錯誤：${data.error}</p>`;
    return;
  }

  resultDiv.innerHTML = `
    <h2>${data.title} (${data.year})</h2>
    <img src="${data.poster_url}" alt="海報" width="200">
    <p><strong>導演：</strong>${data.director}</p>
    <p><strong>平均評分：</strong>${data.average_rating}</p>
    <p><strong>描述：</strong>${data.description}</p>
    <h3>評論：</h3>
    <ul>
      ${data.reviews.map(review => `
        <li>
          <strong>${review.reviewer}</strong> (${review.date})：${review.rating}<br>
          ${review.review_text}<br>
          ❤ ${review.likes} 喜歡
        </li>
      `).join('')}
    </ul>
  `;

  // 銷毀舊圖表
  if (chartInstance) {
    chartInstance.destroy();
  }

  const sortedLabels = Object.keys(data.rating_distribution).sort((a, b) => parseFloat(a) - parseFloat(b));
  const sortedCounts = sortedLabels.map(label => data.rating_distribution[label]);

  chartInstance = new Chart(chartCanvas, {
    type: 'bar',
    data: {
      labels: sortedLabels,
      datasets: [{
        label: '各星等評分數量',
        data: sortedCounts,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});
