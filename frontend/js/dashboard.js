import { get } from './api.js';

async function loadDashboard() {
	try {
		// Backend returns data directly (no wrapper) in snake_case
		const data = await get('/api/dashboard/');

		// Traffic Card
		const trafficIncident = data.traffic.has_incident
			? `<span class="badge badge-warning">⚠️ ${data.traffic.incident_count} Incident(s)</span>`
			: `<span class="badge badge-success">✅ Clear</span>`;

		document.getElementById('trafficCard').innerHTML = `
			<div class="card-header">
				<h3>🚦 Traffic Status</h3>
				${trafficIncident}
			</div>
			<div class="card-body">
				<div class="location-badge" style="background-color: ${data.traffic.status_color}20; color: ${data.traffic.status_color}; border: 2px solid ${data.traffic.status_color};">
					${data.traffic.status_code}
				</div>
				<p class="location"><strong>📍 ${data.traffic.address}</strong></p>
				<div class="mini-stats">
					<div class="mini-stat">
						<span class="mini-label">Speed</span>
						<span class="mini-value">${parseFloat(data.traffic.flow_speed).toFixed(2)} km/h</span>
					</div>
					<div class="mini-stat">
						<span class="mini-label">Delay</span>
						<span class="mini-value">${parseFloat(data.traffic.delay_time).toFixed(2)} min</span>
					</div>
					<div class="mini-stat">
						<span class="mini-label">Congestion</span>
						<span class="mini-value">${parseFloat(data.traffic.congestion_rate).toFixed(2)}%</span>
					</div>
				</div>
				<p class="analysis">${data.traffic.analysis}</p>
				<p class="recommendation"><strong>Recommendation:</strong> ${data.traffic.recommendation}</p>
			</div>
		`;

		// Energy Card
		const anomalyBadge = data.energy.anomalies_detected
			? `<span class="badge badge-error">⚠️ Anomalies Detected</span>`
			: `<span class="badge badge-success">✅ Normal</span>`;

		document.getElementById('energyCard').innerHTML = `
			<div class="card-header">
				<h3>⚡ Energy Status</h3>
				${anomalyBadge}
			</div>
			<div class="card-body">
				<div class="stat-grid">
					<div class="stat-box">
						<div class="stat-label">Total Consumption</div>
						<div class="stat-value">${
							data.energy.total_consumption
						} <span class="unit">kWh</span></div>
					</div>
					<div class="stat-box">
						<div class="stat-label">Average Power</div>
						<div class="stat-value">${data.energy.avg_power.toFixed(
							2
						)} <span class="unit">W</span></div>
					</div>
				</div>
				<div class="voltage-stats">
					<h4>Voltage Statistics</h4>
					<div class="voltage-grid">
						<div><span class="voltage-label">Min:</span> <strong>${
							data.energy.voltage_stats.min
						}V</strong></div>
						<div><span class="voltage-label">Avg:</span> <strong>${
							data.energy.voltage_stats.average
						}V</strong></div>
						<div><span class="voltage-label">Max:</span> <strong>${
							data.energy.voltage_stats.max
						}V</strong></div>
					</div>
				</div>
			</div>
		`;

		// Waste Card
		const criticalBadge =
			data.waste.critical_count > 0
				? `<span class="badge badge-error">🚨 ${data.waste.critical_count} Critical</span>`
				: `<span class="badge badge-success">✅ Normal</span>`;

		const warningSection =
			data.waste.warning_count > 0
				? `
			<div class="warning-locations">
				<h4>⚠️ Warning Locations (${data.waste.warning_count})</h4>
				<ul>
					${data.waste.warning_locations.map((loc) => `<li>${loc}</li>`).join('')}
				</ul>
			</div>
		`
				: '';

		document.getElementById('wasteCard').innerHTML = `
			<div class="card-header">
				<h3>🗑️ Waste Management</h3>
				${criticalBadge}
			</div>
			<div class="card-body">
				<div class="stat-grid">
					<div class="stat-box">
						<div class="stat-label">Average Fill Level</div>
						<div class="stat-value">${data.waste.avg_fill_level}<span class="unit">%</span></div>
					</div>
					<div class="stat-box">
						<div class="stat-label">Critical Bins</div>
						<div class="stat-value-lg">${data.waste.critical_count}</div>
					</div>
				</div>
				${warningSection}
			</div>
		`;

		// Reports Card
		const reportsHtml =
			data.reports.recent && data.reports.recent.length > 0
				? data.reports.recent
						.slice(0, 3)
						.map(
							(report) => `
					<div class="report-item">
						<div class="report-header">
							<span class="report-type">${report.issue_type_display}</span>
							<span class="report-status status-${report.status}">${report.status_display}</span>
						</div>
						<div class="report-location">📍 ${report.location}</div>
						<div class="report-desc">${report.description}</div>
						<div class="report-meta">by ${report.reporter_name}</div>
					</div>
				`
						)
						.join('')
				: '<p class="no-data">No recent reports</p>';

		document.getElementById('reportsCard').innerHTML = `
			<div class="card-header">
				<h3>📝 Citizen Reports</h3>
				<span class="badge badge-info">${data.reports.total_count} Total</span>
			</div>
			<div class="card-body">
				<div class="reports-summary">
					<div class="summary-item">
						<span class="summary-label">Pending</span>
						<span class="summary-value">${data.reports.pending_count}</span>
					</div>
					<div class="summary-item">
						<span class="summary-label">Total</span>
						<span class="summary-value">${data.reports.total_count}</span>
					</div>
				</div>
				<div class="recent-reports">
					<h4>Recent Reports</h4>
					${reportsHtml}
				</div>
			</div>
		`;
	} catch (e) {
		console.error('Dashboard load failed:', e);
		document.querySelectorAll('.card').forEach((card) => {
			card.innerHTML =
				'<div class="error-message">Failed to load data</div>';
		});
	}
}

loadDashboard();
