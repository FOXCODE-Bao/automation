import { post } from './api.js';

document.getElementById('reportForm').onsubmit = async (e) => {
	e.preventDefault();
	const formData = new FormData(e.target);

	try {
		// POST /api/reports/ requires multipart/form-data for image upload
		// Fields: reporter_name, issue_type, description, location, image (File)
		await post('/api/reports/', formData, true);
		alert('✅ Report submitted successfully!');
		e.target.reset();
	} catch (err) {
		alert('❌ Failed to submit report. Please try again.');
		console.error('Report submission error:', err);
	}
};
