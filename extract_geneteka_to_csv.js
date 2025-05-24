(function() {
    'use strict';

    function extractAndDownloadMetricalData() {
        const table = document.getElementById('table_s'); // Get the main table by its ID

        if (!table) {
            console.error("Table with ID 'table_s' not found on this page.");
            alert("Could not find the data table. Please ensure you are on a search results page.");
            return;
        }

        const rows = table.querySelectorAll('tr');
        if (rows.length === 0) {
            alert("No data found in the table to export.");
            return;
        }

        let csv = [];
        const headers = [];
        // Extract headers from thead if it exists, otherwise from the first tr
        const headerRow = table.querySelector('thead tr');
        if (headerRow) {
            headerRow.querySelectorAll('th').forEach(th => {
                headers.push(th.innerText.trim().replace(/"/g, '""')); // Escape double quotes
            });
        } else {
            // Fallback if no thead, assume first row is header
            rows[0].querySelectorAll('th, td').forEach(cell => {
                headers.push(cell.innerText.trim().replace(/"/g, '""'));
            });
        }
        csv.push('"' + headers.join('","') + '"'); // Join headers with comma and wrap in quotes

        // Extract data rows
        for (let i = (headerRow ? 1 : 0); i < rows.length; i++) { // Start from 1 if headers were explicitly taken from thead
            const row = rows[i];
            const rowData = [];
            row.querySelectorAll('td').forEach(cell => {
                let cellText = cell.innerText.trim();
                // Replace multiple spaces with a single space and remove newlines
                cellText = cellText.replace(/\s\s+/g, ' ').replace(/(\r\n|\n|\r)/gm, '');
                // Escape double quotes within the data
                rowData.push(cellText.replace(/"/g, '""'));
            });
            csv.push('"' + rowData.join('","') + '"'); // Join data with comma and wrap in quotes
        }

        const csvString = csv.join('\n');
        const filename = 'metrycal_data.csv';

        // Create a Blob and download the CSV file
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) { // Feature detection for download attribute
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url); // Clean up the URL object
            console.log("Metrical data downloaded successfully as " + filename);
        } else {
            // Fallback for browsers that don't support the download attribute
            alert("Your browser does not support automatic file download. Please copy the data below manually:\n\n" + csvString);
        }
    }

    // Add a button to the page to trigger the function
    function addButton() {
        const existingButton = document.getElementById('downloadMetrycalDataButton');
        if (existingButton) {
            existingButton.remove(); // Remove existing button if it's there from a previous run
        }

        const button = document.createElement('button');
        button.innerText = 'Download Metrical Data as CSV';
        button.id = 'downloadMetrycalDataButton';
        button.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10000;
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        `;
        button.onclick = extractAndDownloadMetricalData;
        document.body.appendChild(button);
        console.log("Download Metrical Data button added.");
    }

    // Run the function to add the button
    addButton();

})();
