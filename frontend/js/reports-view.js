import { get } from './api.js';

let allReports = [];
let filteredReports = [];

// Load and display all reports
async function loadReports() {
	try {
		const data = await get('/api/reports/');
		allReports = Array.isArray(data) ? data : [];
		filteredReports = [...allReports];

		displayAnalysis();
		displayReports(filteredReports);
		setupFilters();
	} catch (error) {
		console.error('Error loading reports:', error);
		document.getElementById('reportsList').innerHTML = `
			<div class="error-message">
				<span class="error-icon">❌</span>
				<p>Unable to load reports. Please try again.</p>
			</div>
		`;
		document.getElementById('reportsAnalysis').innerHTML = `
			<div class="error-message">
				<span class="error-icon">❌</span>
				<p>Unable to load analysis.</p>
			</div>
		`;
	}
}

// Display analysis summary
function displayAnalysis() {
	const analysisContainer = document.getElementById('reportsAnalysis');

	// Calculate statistics
	const total = allReports.length;
	const pending = allReports.filter((r) => r.status === 'pending').length;
	const inProgress = allReports.filter(
		(r) => r.status === 'in_progress'
	).length;
	const resolved = allReports.filter((r) => r.status === 'resolved').length;

	// Count by type
	const byType = allReports.reduce((acc, report) => {
		acc[report.issue_type] = (acc[report.issue_type] || 0) + 1;
		return acc;
	}, {});

	analysisContainer.innerHTML = `
		<div class="dashboard-grid">
			<div class="card">
				<div class="card-header">
					<h3>📊 Overview</h3>
				</div>
				<div class="card-body">
					<div class="stat-grid">
						<div class="stat-box">
							<div class="stat-label">Total Reports</div>
							<div class="stat-value">${total}</div>
						</div>
						<div class="stat-box">
							<div class="stat-label">Pending</div>
							<div class="stat-value">${pending}</div>
						</div>
						<div class="stat-box">
							<div class="stat-label">In Progress</div>
							<div class="stat-value">${inProgress}</div>
						</div>
						<div class="stat-box">
							<div class="stat-label">Resolved</div>
							<div class="stat-value">${resolved}</div>
						</div>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="card-header">
					<h3>📈 By Category</h3>
				</div>
				<div class="card-body">
					<div class="category-stats">
						${Object.entries(byType)
							.map(
								([type, count]) => `
							<div class="category-item">
								<span class="category-label">${formatType(type)}</span>
								<span class="category-value">${count}</span>
								<div class="category-bar">
									<div class="category-bar-fill" style="width: ${(count / total) * 100}%"></div>
								</div>
							</div>
						`
							)
							.join('')}
					</div>
				</div>
			</div>

			<div class="card">
				<div class="card-header">
					<h3>🎯 Resolution Rate</h3>
				</div>
				<div class="card-body">
					<div class="resolution-rate">
						<div class="rate-circle">
							<div class="stat-value-lg">${
								total > 0
									? Math.round((resolved / total) * 100)
									: 0
							}%</div>
						</div>
						<p style="text-align: center; color: rgba(255, 255, 255, 0.95); margin-top: 1rem;">
							${resolved} of ${total} reports resolved
						</p>
					</div>
				</div>
			</div>
		</div>
	`;
}

// Display reports list
function displayReports(reports) {
	const reportsContainer = document.getElementById('reportsList');

	if (reports.length === 0) {
		reportsContainer.innerHTML = `
			<div class="no-data">
				<p>No reports found matching your filters.</p>
			</div>
		`;
		return;
	}

	reportsContainer.innerHTML = reports
		.map(
			(report) => `
		<div class="report-card">
			<div class="report-card-header">
				<div class="report-card-left">
					<span class="report-type-badge">${formatType(report.issue_type)}</span>
					<h3 class="report-location">📍 ${report.location}</h3>
				</div>
				<span class="report-status-badge status-${report.status}">${formatStatus(
				report.status
			)}</span>
			</div>
			
			<div class="report-card-body">
				<p class="report-description">${report.description}</p>
				
				${
					report.image
						? `
					<div class="report-image">
						<img src="${report.image}" alt="Report image" />
					</div>
				`
						: ''
				}
				
				<div class="report-meta">
					<span class="meta-item">👤 ${report.reporter_name}</span>
					<span class="meta-item">📅 ${formatDate(report.created_at)}</span>
					${
						report.updated_at
							? `<span class="meta-item">🔄 Updated: ${formatDate(
									report.updated_at
							  )}</span>`
							: ''
					}
				</div>
			</div>
		</div>
	`
		)
		.join('');
}

// Setup filters
function setupFilters() {
	const statusFilter = document.getElementById('statusFilter');
	const typeFilter = document.getElementById('typeFilter');
	const searchInput = document.getElementById('searchInput');

	const applyFilters = () => {
		filteredReports = allReports.filter((report) => {
			const statusMatch =
				statusFilter.value === 'all' ||
				report.status === statusFilter.value;
			const typeMatch =
				typeFilter.value === 'all' ||
				report.issue_type === typeFilter.value;
			const searchMatch =
				searchInput.value === '' ||
				report.location
					.toLowerCase()
					.includes(searchInput.value.toLowerCase()) ||
				report.description
					.toLowerCase()
					.includes(searchInput.value.toLowerCase());

			return statusMatch && typeMatch && searchMatch;
		});

		displayReports(filteredReports);
	};

	statusFilter.addEventListener('change', applyFilters);
	typeFilter.addEventListener('change', applyFilters);
	searchInput.addEventListener('input', applyFilters);
}

// Helper functions
function formatType(type) {
	const types = {
		traffic: '🚗 Traffic',
		infrastructure: '🏗️ Infrastructure',
		waste: '🗑️ Waste',
		other: '📌 Other',
	};
	return types[type] || type;
}

function formatStatus(status) {
	const statuses = {
		pending: 'Pending',
		in_progress: 'In Progress',
		resolved: 'Resolved',
	};
	return statuses[status] || status;
}

function formatDate(dateString) {
	if (!dateString) return 'N/A';
	const date = new Date(dateString);
	return date.toLocaleDateString('vi-VN', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	});
}

// Load reports on page load
loadReports();
