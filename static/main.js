
//deals with register page
if (window.location.pathname.endsWith("/register")) {
        registerUser()
    } 
 function registerUser() {
    $(document).ready(function(){
        $('#register-btn').click(function(){
            let username = document.querySelector('#user').value;
            let password = document.querySelector('#pass').value;
            let conf_pass = document.querySelector('#confirm-pass').value;
            const error_box = document.getElementById('error-box');
            error_box.innerHTML = "";
            error_box.style.color = "red";
            if (username) {
                if (password.length >= 8) {
                    if (password === conf_pass) {
                        let data = {
                            'username' : username,
                            'password' : password,
                            'confirm_password' : conf_pass
                        }
                        fetch("/verify/register-user", {
                            method: 'post',
                            headers: {"Content-Type" : "application/json"},
                            body: JSON.stringify(data)
                            

                        }).then(res => {
                            if (res.status === 201) { 
                                return res.json();
                            } else if (res.status === 422 || res.status === 409){
                                return res.json() 

                            } else {
                                throw new Error("Unexpected Error!")
                            }
                            
                        }).then(body => {
                            if (body.ok && body.redirect) { 
                                window.location.href = body.redirect

                            } else if (body.fieldErrors) {
                                if (body.fieldErrors.username) { 
                                    error_box.innerHTML = body.fieldErrors.username;
                                } else if (body.fieldErrors.password) {
                                    error_box.innerHTML = body.fieldErrors.password;
                                } else if (body.fieldErrors.confirm_password) { 
                                    error_box.innerHTML = body.fieldErrors.confirm_password
                                }


                            }

                        }).catch(err => {
                            console.error("Host-side error: ", err)
                            error_box.innerHTML = "Something went wrong. Please try again later!"
                            
                        })
                        
                    } else {
                        error_box.innerHTML = "Passwords are not the same!";
                        
                    }

                } else {
                    error_box.innerHTML = "Password length is less than 8!";
                }

            } else {
                error_box.innerHTML = "Username is empty!";
                
            }
        })
    })
} 


    


//deals with login page
if (window.location.pathname.endsWith("/login")) {
     loginUser()


}

function loginUser(){
    $(document).ready(function(){
        $('#login-btn').click(function(){
            let username = document.querySelector('#user').value;
            let password = document.querySelector('#pass').value;
            const chkbox_val = document.querySelector("#remember-checkbox").checked;  
            const error_box = document.getElementById('error-box')
            error_box.style.color = "red";
            let data = {
                'username' : username,
                'password' : password,
                'checkbox' : chkbox_val
            }
            fetch('/verify/login', {
                method : 'post',
                headers : {'Content-Type' : 'application/json'},
                body : JSON.stringify(data)


            }).then(res => {
                if (res.status === 201) { 
                    return res.json()
                } else if (res.status === 401) { 
                    return res.json()
                } else { 
                    throw new Error("Unexpected Err or!")
                }


            }).then(body => { 
                if (body.ok && body.redirect) { 
                    window.location.href = body.redirect
                } else if (body.fieldErrors) {
                    error_box.innerHTML = body.fieldErrors.login_details 

                }
            }).catch(err => {
                            console.error("Host-side error: ", err)
                            error_box.innerHTML = "Something went wrong. Please try again later!"
                            
            }) 
        })

    })
}









