// Contact form: sends to Formspree without leaving the page, with a plain fallback.
(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;
  var status = document.getElementById('form-status');
  var button = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.action.indexOf('FORMSPREE_ID') !== -1) {
      status.textContent = 'The contact form is not active yet. Please reach me on LinkedIn for now.';
      return;
    }
    button.disabled = true;
    status.textContent = 'Sending…';
    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { Accept: 'application/json' }
    }).then(function (res) {
      if (res.ok) {
        form.reset();
        status.textContent = 'Thank you. Your message is on its way and I will reply by email.';
      } else {
        status.textContent = 'Something went wrong. Please try again, or reach me on LinkedIn.';
      }
    }).catch(function () {
      status.textContent = 'Something went wrong. Please try again, or reach me on LinkedIn.';
    }).then(function () {
      button.disabled = false;
    });
  });
})();
