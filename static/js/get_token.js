$(document).ready(function() {
  var access_token = window.location.hash.substr(1);
  console.log('Attempting to grap access token');
  if (access_token) {
    $.ajax({
      url: '/process_token',
      type: 'POST',
      data: { access_token: access_token },
      success: function(response) {
        console.log('Server response:', response);
        window.location.href = '/me';
      },
      error: function(error) {
        console.log('Server error from the JS file:', error);
      }
    });
  }
});