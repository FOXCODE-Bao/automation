import { post } from './api.js';

const subscribeForm = document.getElementById('subscribeForm');

if (subscribeForm) {
	subscribeForm.onsubmit = async (e) => {
		e.preventDefault();
		const email = new FormData(subscribeForm).get('email');

		try {
			await post('/api/subscribe/', { email });
			alert(
				'✅ Successfully subscribed! You will receive traffic alerts at ' +
					email
			);
			subscribeForm.reset();
		} catch (err) {
			alert('❌ Failed to subscribe. Please try again.');
			console.error('Subscribe error:', err);
		}
	};
}
