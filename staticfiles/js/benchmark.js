const form =
document.getElementById(
"benchmarkSearch"
);

if(form){

form.addEventListener(
"submit",

async function(e){

e.preventDefault();

const creditInfo =
await apiRequest(
"/accounts/credits/"
);

if(
creditInfo.credits < 5
){

showCreditModal();

return;

}

const position =
this.position.value;

const data = await apiRequest(
    `/compensation/benchmark/?company=${companyId}&job_title=${position}`
);

document.getElementById(
"benchmarkResult"
).innerHTML = `

<h3>
Median Salary:
${data.median_salary}
</h3>

<p>
P25:
${data.p25}
</p>

<p>
P50:
${data.p50}
</p>

<p>
P75:
${data.p75}
</p>

`;

}

);

}