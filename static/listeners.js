window.addEventListener('load', function(){

    // Get Elements from the HTML document
    var current_password = document.getElementById('password');
    var show_password  = document.getElementById('check');

    show_password.addEventListener('change', function() {

        if(this.checked) {
            current_password.type = 'text';
        } else {
            current_password.type = 'password';
        }

    });

});
