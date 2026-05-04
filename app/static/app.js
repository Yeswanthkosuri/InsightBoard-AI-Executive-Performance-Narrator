/**
 * InsightBoard Report Generator
 * Enhanced vanilla JavaScript with polished interactions
 */

// ── DOM References ──

const form = document.getElementById("report-form");
const submitButton = document.getElementById("submit-button");
const loadingIndicator = document.getElementById("loading-indicator");
const validationMessage = document.getElementById("validation-message");
const errorPanel = document.getElementById("error-panel");
const errorMessage = document.getElementById("error-message");
const resultsPanel = document.getElementById("results-panel");

// Result elements
const resultTitle = document.getElementById("result-title");
const resultMeta = document.getElementById("result-meta");
const executiveSummary = document.getElementById("executive-summary");
const recommendedActions = document.getElementById("recommended-actions");
const anomalyCommentary = document.getElementById("anomaly-commentary");
const trendNarrative = document.getElementById("trend-narrative");
const processingSummary = document.getElementById("processing-summary");
const metricSnapshots = document.getElementById("metric-snapshots");
const chartImagePreview = document.getElementById("chart-image-preview");
const chartEmptyState = document.getElementById("chart-empty-state");
const chartMeta = document.getElementById("chart-meta");
const chartDownloadBtn = document.getElementById("chart-download-btn");
const chartExpandBtn = document.getElementById("chart-expand-btn");
const chartLightbox = document.getElementById("chart-lightbox");
const lightboxClose = document.getElementById("lightbox-close");
const lightboxImg = document.getElementById("lightbox-img");

// File inputs
const csvFileInput = document.getElementById("csv-file");
const chartImageInput = document.getElementById("chart-image");

// File labels
const csvFileLabel = document.getElementById("csv-file-label");
const chartFileLabel = document.getElementById("chart-file-label");

// Drop areas
const csvDroparea = document.getElementById("csv-droparea");
const chartDroparea = document.getElementById("chart-droparea");


// ── Validation ──

function showValidation(message) {
  validationMessage.textContent = message;
  validationMessage.classList.remove("hidden");
  validationMessage.focus();
}

function clearValidation() {
  validationMessage.textContent = "";
  validationMessage.classList.add("hidden");
}

function validateFiles() {
  const csvFile = csvFileInput.files[0];
  const chartFile = chartImageInput.files[0];

  if (!csvFile) {
    showValidation("Please choose a KPI CSV file before generating a report.");
    return false;
  }

  if (!csvFile.name.toLowerCase().endsWith(".csv")) {
    showValidation("The KPI upload must be a .csv file.");
    return false;
  }

  if (chartFile && !chartFile.type.startsWith("image/")) {
    showValidation("The optional chart upload must be an image file.");
    return false;
  }

  clearValidation();
  return true;
}


// ── Error Handling ──

function showError(message) {
  errorMessage.textContent = message;
  errorPanel.classList.remove("hidden");
  errorPanel.scrollIntoView({ behavior: "smooth", block: "center" });
}

function clearError() {
  errorMessage.textContent = "";
  errorPanel.classList.add("hidden");
}


// ── Loading State ──

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  loadingIndicator.classList.toggle("hidden", !isLoading);
  loadingIndicator.setAttribute("aria-busy", isLoading ? "true" : "false");
}


// ── File Upload Enhancement ──

function setupFileInput(input, label, droparea) {
  // Show selected filename
  input.addEventListener("change", () => {
    if (input.files[0]) {
      const name = input.files[0].name;
      const truncated = name.length > 32 ? name.slice(0, 29) + "…" : name;
      label.textContent = truncated;
      label.classList.add("has-file");
      droparea.style.borderColor = "";
    } else {
      label.textContent = "Choose file or drag & drop";
      label.classList.remove("has-file");
    }
    validateFiles();
  });

  // Drag & drop
  ["dragenter", "dragover"].forEach((evt) => {
    droparea.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      droparea.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    droparea.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      droparea.classList.remove("drag-over");
    });
  });

  droparea.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      input.files = files;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });
}

setupFileInput(csvFileInput, csvFileLabel, csvDroparea);
setupFileInput(chartImageInput, chartFileLabel, chartDroparea);


// ── Rendering Utilities ──

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatNumber(value) {
  if (typeof value === "number") {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
      minimumFractionDigits: 0,
    }).format(value);
  }
  return "N/A";
}

function renderList(target, items, emptyMessage) {
  target.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyMessage;
    li.style.opacity = "0.5";
    li.style.fontStyle = "italic";
    target.appendChild(li);
    return;
  }

  items.forEach((item, index) => {
    const li = document.createElement("li");
    li.textContent = item;
    li.style.animation = `fadeInUp 300ms var(--ease-out) ${index * 40}ms both`;
    target.appendChild(li);
  });
}


// ── Render Processing Summary ──

function renderProcessingSummary(report) {
  const rows = [
    ["Records analyzed", report.records_analyzed],
    ["Periods analyzed", report.periods_analyzed],
    ["Aggregation", report.preprocessing_summary?.aggregation_granularity ?? "N/A"],
    ["Missing strategy", report.preprocessing_summary?.missing_value_strategy ?? "N/A"],
    ["Duplicates removed", report.preprocessing_summary?.exact_duplicate_rows_removed ?? "N/A"],
    ["Values imputed", report.preprocessing_summary?.missing_values_imputed ?? "N/A"],
  ];

  processingSummary.innerHTML = rows
    .map(([label, value]) => {
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.textContent = value;
      return dt.outerHTML + dd.outerHTML;
    })
    .join("");
}


// ── Render Metric Snapshots ──

function renderMetricSnapshots(snapshots) {
  metricSnapshots.innerHTML = "";

  if (!Array.isArray(snapshots) || snapshots.length === 0) {
    const p = document.createElement("p");
    p.textContent = "No metric snapshots were returned.";
    p.style.opacity = "0.5";
    p.style.fontStyle = "italic";
    metricSnapshots.appendChild(p);
    return;
  }

  snapshots.forEach((snapshot, index) => {
    const article = document.createElement("article");
    article.className = "metric-card";
    article.style.animation = `fadeInUp 300ms var(--ease-out) ${index * 50}ms both`;

    const direction = snapshot.trend_direction || "flat";
    const trendIcon = direction === "up" ? "↑" : direction === "down" ? "↓" : "→";

    article.innerHTML = `
      <div class="metric-card-header">
        <span>${escapeHtml(snapshot.metric)}</span>
        <span class="trend-badge trend-${direction}">${trendIcon} ${direction}</span>
      </div>
      <div class="metric-card-meta">
        <span><strong>Latest:</strong> ${formatNumber(snapshot.latest_value)}</span>
        <span><strong>Previous:</strong> ${formatNumber(snapshot.previous_value)}</span>
        <span><strong>Change:</strong> ${formatNumber(snapshot.absolute_change)}</span>
        <span><strong>Mean:</strong> ${formatNumber(snapshot.mean_value)}</span>
      </div>
    `;

    metricSnapshots.appendChild(article);
  });
}


// ── Render Chart ──

function renderChart(report) {
  const hasChart = Boolean(report.chart_base64 && report.chart_mime_type);

  if (!hasChart) {
    chartImagePreview.classList.add("hidden");
    chartImagePreview.removeAttribute("src");
    chartEmptyState.classList.remove("hidden");
    chartMeta.textContent = "No chart payload was returned by the API.";
    chartDownloadBtn.classList.add("hidden");
    chartExpandBtn.classList.add("hidden");
    return;
  }

  const dataUrl = `data:${report.chart_mime_type};base64,${report.chart_base64}`;

  chartImagePreview.src = dataUrl;
  chartImagePreview.classList.remove("hidden");
  chartEmptyState.classList.add("hidden");
  chartMeta.textContent = `${report.chart_explanation?.summary ?? "Executive dashboard generated"} (${report.chart_mime_type})`;

  // Show action buttons
  chartDownloadBtn.classList.remove("hidden");
  chartExpandBtn.classList.remove("hidden");

  // Wire Download button
  chartDownloadBtn.onclick = () => {
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `insightboard-dashboard-${Date.now()}.png`;
    a.click();
  };

  // Wire Expand button (lightbox)
  chartExpandBtn.onclick = () => {
    lightboxImg.src = dataUrl;
    chartLightbox.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  };
}


// ── Main Report Renderer ──

function renderReport(report) {
  clearError();

  resultTitle.textContent = report.report_title || "Executive Report";
  resultMeta.textContent = `${report.source_name || "Report"} · ${report.periods_analyzed} periods · ${report.records_analyzed} records`;
  executiveSummary.textContent = report.executive_summary || "No executive summary returned.";

  renderList(
    recommendedActions,
    report.recommended_actions,
    "No recommended actions were returned."
  );
  renderList(
    anomalyCommentary,
    report.anomaly_commentary,
    "No anomaly commentary was returned."
  );
  renderList(
    trendNarrative,
    report.trend_narrative,
    "No trend narrative was returned."
  );

  renderProcessingSummary(report);
  renderMetricSnapshots(report.metric_snapshots);
  renderChart(report);

  resultsPanel.classList.remove("hidden");

  // Smooth scroll to results with a slight delay for animation
  requestAnimationFrame(() => {
    setTimeout(() => {
      resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
  });
}


// ── Form Submission ──

async function submitReport(event) {
  event.preventDefault();
  clearError();

  if (!validateFiles()) {
    return;
  }

  const formData = new FormData(form);

  try {
    setLoading(true);

    const response = await fetch("/api/v1/generate-report", {
      method: "POST",
      body: formData,
    });

    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json()
      : { detail: "The server returned a non-JSON response." };

    if (!response.ok) {
      const detail =
        typeof body.detail === "string"
          ? body.detail
          : "Report generation failed. Please review the upload and try again.";
      throw new Error(detail);
    }

    renderReport(body);
  } catch (error) {
    const errorMsg =
      error instanceof Error
        ? error.message
        : "Unexpected error while generating the report.";
    showError(errorMsg);
  } finally {
    setLoading(false);
  }
}


// ── Event Listeners ──

form.addEventListener("submit", submitReport);

// Lightbox close handlers
function closeLightbox() {
  chartLightbox.classList.add("hidden");
  document.body.style.overflow = "";
}

lightboxClose.addEventListener("click", closeLightbox);
chartLightbox.addEventListener("click", (e) => {
  if (e.target === chartLightbox) closeLightbox();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !chartLightbox.classList.contains("hidden")) {
    closeLightbox();
  }
});


// ── Page Load ──

document.addEventListener("DOMContentLoaded", () => {
  // Stagger hero card animations
  const heroCards = document.querySelectorAll(".hero-card");
  heroCards.forEach((card, i) => {
    card.style.animation = `fadeInUp 400ms var(--ease-out) ${200 + i * 80}ms both`;
  });

  // Animate hero text
  const heroText = document.querySelector(".hero-text");
  if (heroText) {
    heroText.style.animation = "fadeInUp 500ms var(--ease-out) 100ms both";
  }

  // Animate form section
  const formSection = document.querySelector(".form-section");
  if (formSection) {
    formSection.style.animation = "fadeInUp 450ms var(--ease-out) 300ms both";
  }
});
