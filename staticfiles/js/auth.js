const registerForm =
    document.getElementById(
        "registerForm"
    );

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            try {

                const formData = {
                    full_name:
                        this.full_name.value,

                    email:
                        this.email.value,

                    username:
                        this.username.value,

                    password:
                        this.password.value,
                };

                const response =
                    await apiRequest(
                        "/accounts/register/",
                        "POST",
                        formData
                    );

                showToast(
                    response.message ||
                    "Registration successful!",
                    "success"
                );

                setTimeout(() => {

                    window.location.href =
                        "/login/";

                }, 1500);

            } catch (error) {

                console.error(error);

                showToast(
                    "Registration failed",
                    "danger"
                );
            }
        }
    );
}



const loginForm =
    document.getElementById(
        "loginForm"
    );

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            try {

                const formData = {
                    username:
                        this.username.value,

                    password:
                        this.password.value,
                };

                const response =
                    await apiRequest(
                        "/accounts/login/",
                        "POST",
                        formData
                    );

                if (response.access) {

                    localStorage.setItem(
                        "access",
                        response.access
                    );

                    showToast(
                        "Login successful!",
                        "success"
                    );

                    setTimeout(() => {

                        window.location.href =
                            "/";

                    }, 1000);

                } else {

                    showToast(
                        "Login failed",
                        "danger"
                    );
                }

            } catch (error) {

                console.error(error);

                showToast(
                    "Invalid credentials",
                    "danger"
                );
            }
        }
    );
}


document
    .getElementById("profileUpdateForm")
    ?.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            const data = {
                full_name:
                    this.full_name.value,

                username:
                    this.username.value,

                email:
                    this.email.value,
            };

            try {

                const res =
                    await apiRequest(
                        "/accounts/profile/",
                        "PATCH",
                        data
                    );

                console.log(res);

                showToast(
                    "Profile updated successfully",
                    "success"
                );

                setTimeout(() => {
                    location.reload();
                }, 1000);

            } catch (err) {

                console.error(err);

                showToast(
                    JSON.stringify(err),
                    "danger"
                );
            }
        }
    );