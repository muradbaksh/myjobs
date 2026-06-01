const exportCsvBtn =
document.getElementById(
    "exportCsvBtn"
);

if(exportCsvBtn){

    exportCsvBtn.addEventListener(
        "click",
        () => {

            window.location.href =
                "/admin/export/csv/";

        }
    );

}

const exportExcelBtn =
document.getElementById(
    "exportExcelBtn"
);

if(exportExcelBtn){

    exportExcelBtn.addEventListener(
        "click",
        () => {

            window.location.href =
                "/admin/export/excel/";

        }
    );

}