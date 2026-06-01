async function loadUsers() {

    const users = await apiRequest(
        "/admin/users/"
    );

    const container =
        document.getElementById(
            "usersContainer"
        );

    container.innerHTML = "";

    users.forEach(user => {

        container.innerHTML += `

        <div class="user-card">

            <h3>
                ${user.username}
            </h3>

            <p>
                Credits:
                ${user.credits}
            </p>

            <p>
                Role:
                ${user.role}
            </p>

            <button
                onclick="addCredits(${user.id})"
            >
                +10 Credits
            </button>

        </div>

        `;

    });

}

async function addCredits(id){

    await apiRequest(
        `/admin/users/${id}/credits/`,
        "POST",
        {
            amount: 10
        }
    );

    loadUsers();

}

loadUsers();