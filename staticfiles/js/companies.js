let currentPage = 1;

async function loadCompanies() {

    const search = document.getElementById("searchInput")?.value || "";
    const industry = document.getElementById("industryFilter")?.value || "";
    const type = document.getElementById("typeFilter")?.value || "";

    const data = await apiRequest(
        `/companies/?page=${currentPage}&search=${search}&industry=${industry}&company_type=${type}`
    );

    const container = document.getElementById("companiesContainer");

    container.innerHTML = "";

    data.results.forEach(company => {

        container.innerHTML += `
        <div class="company-card">

            <h3>${company.name}</h3>

            <p>Industry: ${company.industry}</p>

            <p>Type: ${company.company_type}</p>

            <p>Reputation: ${company.reputation_index}</p>

            <a href="/companies/${company.slug}/">
                View Details
            </a>

        </div>
        `;
    });
}

loadCompanies();

document.getElementById("searchBtn")?.addEventListener("click", () => {
    currentPage = 1;
    loadCompanies();
});

document.getElementById("industryFilter")?.addEventListener("change", () => {
    currentPage = 1;
    loadCompanies();
});

document.getElementById("typeFilter")?.addEventListener("change", () => {
    currentPage = 1;
    loadCompanies();
});

document.getElementById("nextBtn")?.addEventListener("click", () => {
    currentPage++;
    loadCompanies();
});

document.getElementById("prevBtn")?.addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        loadCompanies();
    }
});