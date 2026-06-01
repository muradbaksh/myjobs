async function loadAuditLogs() {

    const logs = await apiRequest(
        "/admin/reports/"
    );

    const container =
        document.getElementById(
            "reportsContainer"
        );

    container.innerHTML = "";

    logs.forEach(log => {

        container.innerHTML += `

        <div class="audit-card">

            <p>
                User:
                ${log.user}
            </p>

            <p>
                Action:
                ${log.action}
            </p>

            <p>
                Object:
                ${log.object_type}
            </p>

            <p>
                ${log.created_at}
            </p>

        </div>

        `;

    });

}

loadAuditLogs();