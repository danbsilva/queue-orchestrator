$(document).ready(function () {
    'use strict';

    // Login
    $('.bg-gradient-primary').on('submit', "#LoginForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
          type: "POST",
          url: Flask.url_for('auth.login'),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for(data);
          },
          complete: function () {
          },
          error: function(data) {
           highlightErrors(data);
          }
        });
    });

    // Logout
    $('.layout-page').on('click', ".logout", function(e) {
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('auth.logout'),
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for(data);
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });
});

