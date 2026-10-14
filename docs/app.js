
"use strict";

const DATA_URL = "bonuses.json";

const tableBody = document.getElementById("bonus-table");
const statusText = document.getElementById("status");
const countText = document.getElementById("count");
const updatedText = document.getElementById("updated");

function addCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value || "Not stated";
  row.appendChild(cell);
  return cell;
}

async function loadBonuses() {
  try {
    const response = await fetch(DATA_URL);

    if (!response.ok) {
      throw new Error(`Could not load JSON (HTTP ${response.status})`);
    }

    const data = await response.json();
    const casinos = Array.isArray(data.casinos) ? data.casinos : [];

    tableBody.replaceChildren();

    for (const casino of casinos) {
      const row = document.createElement("tr");

      addCell(row, casino.casino);
      addCell(row, casino.welcome_bonus);

      const wagering =
        casino.wagering_requirement ||
        (casino.wagering_multiplier != null
          ? `${casino.wagering_multiplier}x${
              casino.wagering_note ? ` — ${casino.wagering_note}` : ""
            }`
          : null);

      addCell(row, wagering);
      addCell(row, casino.min_deposit);

      const sourceCell = document.createElement("td");
      const link = document.createElement("a");

      link.href = casino.source_url || data.source || "#";
      link.textContent = "View source";
      link.className = "source-link";
      link.target = "_blank";
      link.rel = "noopener noreferrer";

      sourceCell.appendChild(link);
      row.appendChild(sourceCell);
      tableBody.appendChild(row);
    }

    countText.textContent =
      `${casinos.length} ${casinos.length === 1 ? "casino" : "casinos"}`;

    statusText.textContent = casinos.length
      ? "Bonus information loaded from the generated JSON file."
      : "No casino records were found.";

    updatedText.textContent = data.scraped_at
      ? `Data last generated: ${new Date(data.scraped_at).toLocaleString()}`
      : "";

    if (!casinos.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.textContent = "No data available.";
      row.appendChild(cell);
      tableBody.appendChild(row);
    }
  } catch (error) {
    console.error(error);
    statusText.textContent = "Unable to load the bonus data.";
    countText.textContent = "Unavailable";

    tableBody.replaceChildren();

    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent =
      "Could not load the JSON file. Run the page through a local web server and check the data file path.";
    row.appendChild(cell);
    tableBody.appendChild(row);
  }
}

loadBonuses();
