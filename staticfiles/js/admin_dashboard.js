async function loadAdminDashboard() {

    try {

        const data = await apiRequest(
            "/admin/dashboard/stats/"
        );

        document.getElementById(
            "adminDashboardContainer"
        ).innerHTML = `

            <div class="stat-card">
                <h3>${data.total_users}</h3>
                <p>Total Users</p>
            </div>

            <div class="stat-card">
                <h3>${data.total_companies}</h3>
                <p>Total Companies</p>
            </div>

            <div class="stat-card">
                <h3>${data.total_reviews}</h3>
                <p>Total Reviews</p>
            </div>

            <div class="stat-card">
                <h3>${data.pending_reports}</h3>
                <p>Pending Reports</p>
            </div>

        `;

    } catch(error){

        console.error(error);

    }

}

document.addEventListener(
    "DOMContentLoaded",
    loadAdminDashboard
);