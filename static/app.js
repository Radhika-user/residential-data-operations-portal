let previewController = null;

function showLoader() {
    document.getElementById("loader").classList.remove("hidden");
}

function hideLoader() {
    document.getElementById("loader").classList.add("hidden");
}

function showSuccess(msg) {
    let box = document.getElementById("msg");
    box.className = "message success";
    box.innerText = msg;
}

function showError(msg) {
    let box = document.getElementById("msg");
    box.className = "message error";
    box.innerText = msg;
}

function runSP() {
    showLoader();

    let formData = new FormData();
    formData.append(
        "sp_name",
        document.getElementById("spSelect").value
    );

    fetch("/run_sp", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();

        if (data.status === "success") {
            showSuccess(data.message);
            loadHistory();
        } else {
            showError(data.message);
        }
    })
    .catch(() => {
        hideLoader();
        showError("SP execution failed");
    });
}

function previewTaxRoll() {
    showLoader();

    previewController = new AbortController();

    let formData = new FormData();
    formData.append(
        "cad_account",
        document.getElementById("cadAccountNumber").value
    );
    formData.append(
        "prop_address",
        document.getElementById("propAddress").value
    );
    formData.append(
        "parcel_id",
        document.getElementById("parcelId").value
    );
    formData.append(
        "cad_id",
        document.getElementById("cadId").value
    );

    fetch("/preview_taxroll", {
        method: "POST",
        body: formData,
        signal: previewController.signal
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();

        if (data.status === "success") {
            showSuccess("Preview loaded successfully");
            renderGrid(data.columns, data.data);
            loadHistory();
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        hideLoader();

        if (error.name !== "AbortError") {
            showError("Request failed");
        }
    });
}

function renderGrid(columns, rows) {
    let html = "<table><tr>";

    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });

    html += "</tr>";

    rows.forEach(row => {
        html += "<tr>";
        columns.forEach(col => {
            html += `<td>${row[col]}</td>`;
        });
        html += "</tr>";
    });

    html += "</table>";

    document.getElementById("grid").innerHTML = html;
}

function loadHistory() {
    fetch("/history")
    .then(response => response.json())
    .then(data => {
        let html = "";

        data.forEach(row => {
            html += `
                <tr>
                    <td>${row.action}</td>
                    <td>${row.source}</td>
                    <td>${row.status}</td>
                    <td>${row.time}</td>
                </tr>
            `;
        });

        document.getElementById("historyBody").innerHTML = html;
    });
}

function downloadExcel() {
    let params = new URLSearchParams();
    params.append(
        "cad_account",
        document.getElementById("cadAccountNumber").value
    );
    params.append(
        "prop_address",
        document.getElementById("propAddress").value
    );
    params.append(
        "parcel_id",
        document.getElementById("parcelId").value
    );
    params.append(
        "cad_id",
        document.getElementById("cadId").value
    );

    window.location.href =
        "/download_excel?" + params.toString();

    showSuccess("Excel download started");
}

function downloadCSV() {
    let params = new URLSearchParams();
    params.append(
        "cad_account",
        document.getElementById("cadAccountNumber").value
    );
    params.append(
        "prop_address",
        document.getElementById("propAddress").value
    );
    params.append(
        "parcel_id",
        document.getElementById("parcelId").value
    );
    params.append(
        "cad_id",
        document.getElementById("cadId").value
    );

    window.location.href =
        "/download_csv?" + params.toString();

    showSuccess("CSV download started");
}

function resetFields() {
    document.getElementById("cadAccountNumber").value = "";
    document.getElementById("propAddress").value = "";
    document.getElementById("parcelId").value = "";
    document.getElementById("cadId").value = "";
    document.getElementById("grid").innerHTML = "";
    showSuccess("Fields reset successfully");
}

function stopRunning() {
    if (previewController) {
        previewController.abort();
        hideLoader();
        showError("Operation stopped");
    }
}

window.onload = function () {
    loadHistory();
}
