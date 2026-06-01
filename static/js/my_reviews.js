async function loadMyReviews(){

    const data =
        await apiRequest(
            "/reviews/my/"
        );

    const container =
        document.getElementById(
            "reviewsContainer"
        );

    container.innerHTML = "";

    data.forEach(review => {

        container.innerHTML += `

        <div class="review-card">

            <span>
                🕶 Anonymous Verified
            </span>

            <h3>
                ${review.company_name}
            </h3>

            <p>
                ${review.comment}
            </p>

        </div>

        `;

    });

}

loadMyReviews();