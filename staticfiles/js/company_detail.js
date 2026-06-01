const companyId =
    window.location.pathname
    .split("/")
    .filter(Boolean)
    .pop();

async function loadCompany() {

    const company =
        await apiRequest(
            `/companies/${companyId}/`
        );

    document.getElementById(
        "companyName"
    ).innerText =
        company.name;

    document.getElementById(
        "companyInfo"
    ).innerHTML = `

        <p>
            Industry:
            ${company.industry}
        </p>

        <p>
            Company Type:
            ${company.company_type}
        </p>

        <p>
            Location:
            ${company.headquarters}
        </p>

        <p>
            Employees:
            ${company.manpower_size}
        </p>

    `;

    document.getElementById(
        "reputationContainer"
    ).innerHTML = `

        <h1>
            ${company.reputation_index}/10
        </h1>

    `;

    document.getElementById(
        "categoryScoresContainer"
    ).innerHTML = `

        <div class="score-card">
            Brand Value:
            ${company.brand_value_score || "-"}
        </div>

        <div class="score-card">
            Work Environment:
            ${company.work_environment_score || "-"}
        </div>

        <div class="score-card">
            Career Growth:
            ${company.career_growth_score || "-"}
        </div>

        <div class="score-card">
            Salary Satisfaction:
            ${company.salary_score || "-"}
        </div>

        <div class="score-card">
            Benefits:
            ${company.benefits_score || "-"}
        </div>

        <div class="score-card">
            Work Life Balance:
            ${company.work_life_balance_score || "-"}
        </div>

    `;

    const reviewsContainer =
        document.getElementById(
            "reviewsContainer"
        );

    reviewsContainer.innerHTML = "";

    company.recent_reviews.forEach(
        review => {

            reviewsContainer.innerHTML += `

            <div class="review-card">

                <span>
                    🕶 Anonymous
                </span>

                <p>
                    ${review.comment}
                </p>

            </div>

            `;

        }
    );

    document.getElementById(
        "compensationContainer"
    ).innerHTML = `

        <div class="card">

            <p>
                Median Salary:
                ${company.median_salary || "-"}
            </p>

            <p>
                P25:
                ${company.p25_salary || "-"}
            </p>

            <p>
                P50:
                ${company.p50_salary || "-"}
            </p>

            <p>
                P75:
                ${company.p75_salary || "-"}
            </p>

        </div>

    `;
}

loadCompany();