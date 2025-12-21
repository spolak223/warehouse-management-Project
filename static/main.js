
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
                    throw new Error("Unexpected Error!")
                }


            }).then(body => { 
                if (body.ok && body.redirect) { 
                    window.location.href = body.redirect
                } else if (body.fieldErrors) {
                    error_box.innerHTML = body.fieldErrors.login_details 

                }
            }).catch(err => {
                            console.error("Host-side error: ", err)
                            
                            
            }) 
        })

    })
}

if (window.location.pathname.endsWith("/admin/manage_admins")) {
    selectAdmin()
    

}

function selectAdmin() {
    const all_rows = document.querySelectorAll("tbody tr");
    let highlight_row = null;
    let text = "";
    let selected_user = null;


    
    for (let i = 0; i < all_rows.length; i++) {
        
        all_rows[i].addEventListener("click", async function(event) {
            event.stopPropagation();

           

            if (highlight_row !== null && highlight_row !== all_rows[i]) {
                highlight_row.classList.remove("select");
                selected_user = null
            }

            all_rows[i].classList.toggle("select")

            if (all_rows[i].classList.contains("select")) { 
                highlight_row = all_rows[i]
                text = highlight_row.textContent.trim().replace(/\s+/g, " ")
                if (selected_user === null) { 
                    selected_user = text

                } else if (selected_user !== null) { 
                    selected_user = text
                }

            }
            else { 
                highlight_row = null;
                text = ""
                selected_user = null
            }

            

            
            
        })
    }
    $(document).ready(function(){ 
        $("#appoint-admin").click(async function() {
            await appoint_admin(selected_user)


        })
    })

    $(document).ready(function() { 
        $("#remove-admin").click(async function(){ 
            await remove_admin(selected_user)

        })
    })
}

async function appoint_admin(text) { 
                let data = {
                    "action" : "appoint",
                    "user_and_role" : text 

                }


                await fetch("/admin/manage_admins", {
                    method : "POST",
                    headers : {"Content-Type" : "application/json"},
                    body : JSON.stringify(data) 
                    }    
                ).then(res => { 
                    if (res.status === 201) {
                        window.location.reload();
                        return res.json() 

                    } else if (res.status === 405){ 
                        return res.json()

                    } else { 
                        throw new Error("Unexpected error!")
                    }
                    
                        
                }

                ).then(body => { 
                    if (body.fieldErrors) { 
                        ErrorHandlerAdmins(body.fieldErrors.appointing, 1500)
                        
                    }
                })
            }
        

async function remove_admin(text) { 
            let data = {
                "action" : "remove",
                "user_and_role" : text
            }
            await fetch("/admin/manage_admins", { 
                method : "POST",
                headers : {"Content-Type" : "application/json"},
                body : JSON.stringify(data)
            }).then(res => { 
                if (res.status === 201) { 
                    window.location.reload()
                    return res.json()
                } else if (res.status === 405) { 
                    return res.json()
                } else { 
                    throw new Error("Unexpected Error!")
                }
            }).then(body => { 
                if (body.fieldErrors) { 
                    ErrorHandlerAdmins(body.fieldErrors.removing, 1500)
                }
            })
        }


function ErrorHandlerAdmins(error_msg, duration_ms) {
    const error_box = document.getElementById("manager_error_box")
    error_box.style.color = "red";
    error_box.innerHTML = error_msg;

    setTimeout(() => {
        manager_error_box.innerHTML = "";
    }, duration_ms)


}

function ErrorHandlerOrders(error_message){
    const error_box = document.getElementById("error_box")
    error_box.style.color = "red";
    error_box.innerHTML = error_message;

    setTimeout(() => {
        error_box.innerHTML = "";

    }, 2000)

}

if (window.location.pathname.includes("/admin/create_order")) { 
    const customer_form = document.getElementById("customer_order")
    if (customer_form) {
        customer_form.addEventListener("submit", handle_get_order)
    }
}



async function handle_get_order(event) {
    console.log("here!")
    event.preventDefault()
    let form = document.getElementById("customer_order")
    let customer_order = new FormData(form)

    let sku = customer_order.get("p_id")
    let order_qty = customer_order.get("q_ordered")
    let product_type = customer_order.get("p_type") 
    let order_date = customer_order.get("o_date")

    let main_url = "/admin/verify_order"
    let url = main_url + "?sku=" + encodeURIComponent(sku) + "&qty=" + encodeURIComponent(order_qty) + "&type=" + encodeURIComponent(product_type) + "&date=" + encodeURIComponent(order_date)
    
    const res = await fetch(url, {
        method : "GET"
    })
    const data = await res.json()
    console.log(data)
    if (data.ok) { 
        console.log("Nope all good!")
        form.submit()
    } else {
        console.log("ERRROR!")
        ErrorHandlerOrders(data.fieldErrors.error) 

    }

    

}









