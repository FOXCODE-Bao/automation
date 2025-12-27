import { post } from './api.js';

const btn = document.getElementById('checkBtn');
const resultContainer = document.getElementById('resultContainer');
const result = document.getElementById('result');
const loading = document.getElementById('loading');

btn.onclick = async () => {
	const location = document.getElementById('roadName').value.trim();
	if (!location) return alert('Please enter a location!');

	loading.classList.remove('hidden');
	resultContainer.classList.add('hidden');
	result.textContent = '';

	try {
		const res = await post('/api/check-traffic/', {
			location: location,
		});

		// Backend returns data directly in camelCase
		const data = res;

		// Build comprehensive result display
		const incidentBadge = data.hasIncident
			? `<span class="badge badge-warning">⚠️ ${data.incidentCount} Incident(s)</span>`
			: `<span class="badge badge-success">✅ No Incidents</span>`;

		const statusBadge = `<span class="status-badge" style="background-color: ${data.statusColor}; color: white;">${data.statusCode}</span>`;

		result.innerHTML = `
			<div class="result-header">
				<h2>📍 ${data.address}</h2>
				<div class="badges">
					${statusBadge}
					${incidentBadge}
				</div>
			</div>

			<div class="traffic-stats">
				<div class="stat-item">
					<div class="stat-icon">📈</div>
					<div class="stat-info">
						<div class="stat-label">Congestion Rate</div>
						<div class="stat-value">${parseFloat(data.congestionRate).toFixed(2)}%</div>
					</div>
				</div>
				<div class="stat-item">
					<div class="stat-icon">🚗</div>
					<div class="stat-info">
						<div class="stat-label">Flow Speed</div>
						<div class="stat-value">${data.flowSpeed} km/h</div>
					</div>
				</div>
				<div class="stat-item">
					<div class="stat-icon">⏱️</div>
					<div class="stat-info">
						<div class="stat-label">Delay Time</div>
						<div class="stat-value">${data.delayTime} min</div>
					</div>
				</div>
			</div>

			<div class="analysis-section">
				<h3>📊 Analysis</h3>
				<p>${data.analysis}</p>
			</div>

			<div class="recommendation-section">
				<h3>💡 Recommendation</h3>
				<p>${data.recommendation}</p>
			</div>

			${
				data.alternativeRoutes && data.alternativeRoutes.length > 0
					? `
				<div class="routes-section">
					<h3>🛣️ Alternative Routes</h3>
					<ul class="routes-list">
						${data.alternativeRoutes.map((route) => `<li>${route}</li>`).join('')}
					</ul>
				</div>
			`
					: ''
			}
		`;

		resultContainer.classList.remove('hidden');
	} catch (e) {
		result.innerHTML = `
			<div class="error-message">
				<span class="error-icon">❌</span>
				<p>Unable to check traffic conditions. Please try again.</p>
			</div>
		`;
		resultContainer.classList.remove('hidden');
	} finally {
		loading.classList.add('hidden');
	}
};
