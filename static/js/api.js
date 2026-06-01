// const API_BASE = "/api";

// function getToken() {
//     return localStorage.getItem("access");
// }

// function getCSRFToken() {

//     return document
//         .querySelector(
//             'meta[name="csrf-token"]'
//         )
//         ?.getAttribute("content");
// }

// async function apiRequest(
//     url,
//     method = "GET",
//     data = null
// ) {

//     const headers = {
//         "Content-Type": "application/json",
//     };

//     // JWT Token
//     const token = getToken();

//     if (token) {

//         headers["Authorization"] =
//             `Bearer ${token}`;
//     }

//     // CSRF Token
//     const csrfToken = getCSRFToken();

//     if (csrfToken) {

//         headers["X-CSRFToken"] =
//             csrfToken;
//     }

//     const config = {
//         method,
//         headers,
//     };

//     if (data) {

//         config.body =
//             JSON.stringify(data);
//     }

//     const response = await fetch(
//         API_BASE + url,
//         config
//     );

//     return response.json();
// }



const API_BASE = "/api";

function getToken() {
    return localStorage.getItem("access");
}

function getCSRFToken() {

    return document
        .querySelector(
            'meta[name="csrf-token"]'
        )
        ?.getAttribute("content");
}

async function apiRequest(
    url,
    method = "GET",
    data = null
) {

    const headers = {
        "Content-Type": "application/json",
    };

    const token = getToken();

    if (token) {

        headers["Authorization"] =
            `Bearer ${token}`;
    }

    const csrfToken = getCSRFToken();

    if (csrfToken) {

        headers["X-CSRFToken"] =
            csrfToken;
    }

    const config = {
        method,
        headers,
    };

    if (data) {

        config.body =
            JSON.stringify(data);
    }

    const response = await fetch(
        API_BASE + url,
        config
    );

    const result =
        await response.json();

    if (!response.ok) {

        console.error(
            "API Error:",
            result
        );

        throw result;
    }

    return result;
}
