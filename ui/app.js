/**
 * ==============================================================================
 * CAMPUS LOST AND FOUND MANAGEMENT SYSTEM (LFMS) — FRONTEND CONTROLLER
 * Clean, modern Vanilla JavaScript application with Role-Based Access Control.
 * Supports Student / Campus User portal and Property Officer (Admin) portal.
 * ==============================================================================
 */

// Application State
const state = {
  items: [],
  claims: [],
  lockers: [],
  audit: [],
  analytics: null,
  selectedClaim: null,
  isLiveApi: false,
  userRole: localStorage.getItem("lfms-user-role") || "user", // "user" or "admin"
  metrics: {
    total_items: 0,
    in_custody: 0,
    pending_claims: 0,
    total_valuation: 0,
    reunited_count: 0
  }
};

// Formula variables for RPN Evaluator
let rpnVariables = {
  desc_match: 85,
  serial_match: 95,
  photo_match: 90
};

// Offline Seed Data Fallback
const OFFLINE_SEED_ITEMS = [
  {
    item_id: 1,
    title: "MacBook Pro 14 M2 Space Gray",
    category: "Electronics",
    description: "Left in Library 2nd floor silent study area, has sticker 'Code is Poetry'",
    item_type: "FOUND",
    location: "Central Library 2nd Floor",
    status: "IN_CUSTODY",
    reporter_name: "Aarav Sharma",
    reporter_contact: "aarav.sharma@campus.edu",
    reward_or_value: 125000.0,
    reported_date: "2026-09-02 10:15:00",
    locker_code: "LOCKER-A101"
  },
  {
    item_id: 2,
    title: "Leather Bifold Wallet (Brown)",
    category: "Keys/Wallets",
    description: "Found under table 14 with student ID and transit pass",
    item_type: "FOUND",
    location: "Student Cafeteria",
    status: "IN_CUSTODY",
    reporter_name: "Priya Patel",
    reporter_contact: "priya.patel@campus.edu",
    reward_or_value: 2500.0,
    reported_date: "2026-09-08 13:45:00",
    locker_code: "LOCKER-B204"
  },
  {
    item_id: 3,
    title: "Sony WH-1000XM5 Wireless Headphones",
    category: "Electronics",
    description: "Black over-ear headphones misplaced in CS Seminar Room",
    item_type: "LOST",
    location: "CS Block Room 302",
    status: "REPORTED",
    reporter_name: "Dr. Ramesh Rao",
    reporter_contact: "ramesh.rao@campus.edu",
    reward_or_value: 28000.0,
    reported_date: "2026-09-14 16:20:00",
    locker_code: null
  },
  {
    item_id: 4,
    title: "Campus ID Card & Bus Pass",
    category: "Documents/Cards",
    description: "ID #2026CS409 belonging to Ananya Iyer",
    item_type: "FOUND",
    location: "Sports Complex",
    status: "VERIFIED_RETURNED",
    reporter_name: "Security Desk",
    reporter_contact: "security@campus.edu",
    reward_or_value: 500.0,
    reported_date: "2026-09-19 11:10:00",
    locker_code: "LOCKER-C301",
    release_date: "2026-09-25"
  },
  {
    item_id: 5,
    title: "Blue Hydro Flask Water Bottle",
    category: "Clothing/Apparel",
    description: "32oz vacuum insulated bottle with campus sticker",
    item_type: "FOUND",
    location: "Central Library",
    status: "IN_CUSTODY",
    reporter_name: "Librarian",
    reporter_contact: "library@campus.edu",
    reward_or_value: 1800.0,
    reported_date: "2026-09-22 15:30:00",
    locker_code: "LOCKER-A102"
  },
  {
    item_id: 6,
    title: "Casio FX-991EX Scientific Calculator",
    category: "Electronics",
    description: "ClassWiz calculator in black cover, lost after midterms",
    item_type: "LOST",
    location: "CS Block Lab 2",
    status: "REPORTED",
    reporter_name: "Kavya Menon",
    reporter_contact: "kavya.menon@campus.edu",
    reward_or_value: 1500.0,
    reported_date: "2026-09-24 17:00:00",
    locker_code: null
  }
];

const OFFLINE_SEED_CLAIMS = [
  {
    claim_id: 1,
    item_id: 1,
    claimant_name: "Aarav Sharma",
    claimant_contact: "aarav.sharma@campus.edu",
    proof_description: "Apple ID serial ends in 9942, lockscreen has cat photo, sticker matches",
    confidence_score: 95.0,
    claim_status: "PENDING",
    submitted_at: "2026-09-03 14:20:00",
    item_title: "MacBook Pro 14 M2 Space Gray",
    item_category: "Electronics",
    locker_code: "LOCKER-A101"
  },
  {
    claim_id: 2,
    item_id: 2,
    claimant_name: "Priya Patel",
    claimant_contact: "priya.patel@campus.edu",
    proof_description: "Driving license inside billfold with initials PP, metro card #8831",
    confidence_score: 98.0,
    claim_status: "PENDING",
    submitted_at: "2026-09-09 09:15:00",
    item_title: "Leather Bifold Wallet (Brown)",
    item_category: "Keys/Wallets",
    locker_code: "LOCKER-B204"
  }
];

// Document Elements
let el = {};

function initElements() {
  el = {
    dbEngineLabel: document.getElementById("db-engine-label"),
    themeToggleBtn: document.getElementById("theme-toggle-btn"),
    metricsGrid: document.getElementById("metrics-grid"),
    kpiTotalItems: document.getElementById("kpi-total-items"),
    kpiInCustody: document.getElementById("kpi-in-custody"),
    kpiPendingClaims: document.getElementById("kpi-pending-claims"),
    kpiReturnedCount: document.getElementById("kpi-returned-count"),
    badgeItemsCount: document.getElementById("badge-items-count"),
    badgeClaimsCount: document.getElementById("badge-claims-count"),
    badgeLockersCount: document.getElementById("badge-lockers-count"),
    badgeAuditCount: document.getElementById("badge-audit-count"),
    itemsContainer: document.getElementById("items-container"),
    itemDetailContainer: document.getElementById("item-detail-container"),
    searchInventory: document.getElementById("search-inventory"),
    filterType: document.getElementById("filter-type"),
    filterStatus: document.getElementById("filter-status"),
    filterCategory: document.getElementById("filter-category"),
    btnRefreshInventory: document.getElementById("btn-refresh-inventory"),
    queueItemsContainer: document.getElementById("queue-items-container"),
    selectedClaimTag: document.getElementById("selected-claim-tag"),
    sliderDescMatch: document.getElementById("slider-desc-match"),
    sliderSerialMatch: document.getElementById("slider-serial-match"),
    sliderPhotoMatch: document.getElementById("slider-photo-match"),
    valDescMatch: document.getElementById("val-desc-match"),
    valSerialMatch: document.getElementById("val-serial-match"),
    valPhotoMatch: document.getElementById("val-photo-match"),
    calculatedScoreDisplay: document.getElementById("calculated-score-display"),
    decisionText: document.getElementById("decision-text"),
    btnSettleApprove: document.getElementById("btn-settle-approve"),
    btnSettleReject: document.getElementById("btn-settle-reject"),
    lockersContainer: document.getElementById("lockers-container"),
    categoryAnalyticsTbody: document.getElementById("category-analytics-tbody"),
    auditTimelineContainer: document.getElementById("audit-timeline-container"),
    stackCountTag: document.getElementById("stack-count-tag"),
    btnUndoAction: document.getElementById("btn-undo-action"),
    btnReportItem: document.getElementById("btn-report-item"),
    btnNewClaimTrigger: document.getElementById("btn-new-claim-trigger"),
    modalReportItem: document.getElementById("modal-report-item"),
    modalSubmitClaim: document.getElementById("modal-submit-claim"),
    formReportItem: document.getElementById("form-report-item"),
    formSubmitClaim: document.getElementById("form-submit-claim"),
    claimItemSelect: document.getElementById("claim-item-select"),
    toastContainer: document.getElementById("toast-container") || document.body
  };
}

// ==============================================================================
// INITIALIZATION & EVENT LISTENERS
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
  initElements();
  initTheme();
  initAuth();
  setupModals();
  setupEvaluatorSliders();
  setupSearchAndFilters();
  setupItemDetail();

  // Load initial data
  loadAllData();
});

// Role-Based Auth Handling
function initAuth() {
  const role = state.userRole;
  if (role === "admin") {
    document.body.classList.add("is-admin");
  } else {
    document.body.classList.remove("is-admin");
  }

  // Inject or update user role switcher in header
  const headerActions = document.querySelector(".header-actions");
  if (headerActions && !document.getElementById("auth-role-link")) {
    const roleLink = document.createElement("a");
    roleLink.id = "auth-role-link";
    roleLink.href = "login.html";
    roleLink.className = "user-role-pill";
    roleLink.title = "Click to switch role or portal";
    roleLink.innerHTML = role === "admin"
      ? `<span class="role-badge-tag role-admin">Admin Desk</span> <span>Officer</span>`
      : `<span class="role-badge-tag role-user">Student Portal</span> <span>Switch Role</span>`;
    headerActions.insertBefore(roleLink, headerActions.firstChild);
  }

  // Gatekeeping on admin pages
  const path = window.location.pathname;
  const isAdminPage = path.endsWith("claims.html") || path.endsWith("lockers.html") || path.endsWith("audit.html");
  if (isAdminPage && role !== "admin") {
    const main = document.querySelector("main.container");
    if (main) {
      main.innerHTML = `
        <div class="restricted-banner">
          <div style="font-size: 2.2rem; margin-bottom: 12px;">🛡️</div>
          <h3>Property Custody Officer Portal Required</h3>
          <p>
            Claim verification, match confidence evaluation, locker allocations, and audit history operations 
            are strictly restricted to authorized campus staff officers.
          </p>
          <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <a href="login.html" class="btn btn-primary">Sign in as Custody Officer</a>
            <a href="items.html" class="btn btn-secondary">Browse Public Directory</a>
          </div>
        </div>
      `;
    }
  }
}

// Theme handling
function initTheme() {
  const savedTheme = localStorage.getItem("lfms-theme") || "dark";
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
  }

  if (el.themeToggleBtn) {
    el.themeToggleBtn.addEventListener("click", () => {
      document.body.classList.toggle("light-theme");
      const isLight = document.body.classList.contains("light-theme");
      localStorage.setItem("lfms-theme", isLight ? "light" : "dark");
      showToast(`Switched to ${isLight ? "Light" : "Dark"} theme`, "info");
    });
  }
}

// Modal handling
let modalReturnFocus = null;

function openModal(modal) {
  if (!modal) return;
  modalReturnFocus = document.activeElement;
  modal.classList.add("open");
  const firstField = modal.querySelector("input, select, textarea");
  if (firstField) firstField.focus();
}

function closeModal(modal) {
  if (!modal) return;
  modal.classList.remove("open");
  if (modalReturnFocus && document.contains(modalReturnFocus)) modalReturnFocus.focus();
  modalReturnFocus = null;
}

function setupModals() {
  if (el.btnReportItem && el.modalReportItem) {
    el.btnReportItem.addEventListener("click", () => openModal(el.modalReportItem));
  }

  if (el.btnNewClaimTrigger && el.modalSubmitClaim) {
    el.btnNewClaimTrigger.addEventListener("click", () => {
      populateClaimSelectDropdown();
      openModal(el.modalSubmitClaim);
    });
  }

  document.querySelectorAll("[data-close]").forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-close");
      const modal = document.getElementById(modalId);
      if (modal) closeModal(modal);
    });
  });

  document.addEventListener("keydown", (e) => {
    const modal = document.querySelector(".modal-overlay.open");
    if (!modal) return;
    if (e.key === "Escape") {
      closeModal(modal);
      return;
    }
    if (e.key === "Tab") {
      const focusable = [...modal.querySelectorAll("button, input, select, textarea")].filter(f => !f.disabled);
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  if (el.formReportItem) el.formReportItem.addEventListener("submit", handleReportItemSubmit);
  if (el.formSubmitClaim) el.formSubmitClaim.addEventListener("submit", handleSubmitClaimSubmit);
  if (el.btnUndoAction) el.btnUndoAction.addEventListener("click", handleUndoAction);
}

// Evaluator Sliders
function setupEvaluatorSliders() {
  if (!el.sliderDescMatch) return;

  const updateEvaluator = () => {
    rpnVariables.desc_match = parseFloat(el.sliderDescMatch.value);
    rpnVariables.serial_match = parseFloat(el.sliderSerialMatch.value);
    rpnVariables.photo_match = parseFloat(el.sliderPhotoMatch.value);

    if (el.valDescMatch) el.valDescMatch.textContent = `${rpnVariables.desc_match}%`;
    if (el.valSerialMatch) el.valSerialMatch.textContent = `${rpnVariables.serial_match}%`;
    if (el.valPhotoMatch) el.valPhotoMatch.textContent = `${rpnVariables.photo_match}%`;

    const score = (rpnVariables.desc_match * 0.4) + (rpnVariables.serial_match * 0.4) + (rpnVariables.photo_match * 0.2);
    if (el.calculatedScoreDisplay) el.calculatedScoreDisplay.textContent = `${score.toFixed(2)}%`;

    const passed = score >= 75.0;
    if (el.calculatedScoreDisplay) el.calculatedScoreDisplay.classList.toggle("is-fail", !passed);
    if (el.decisionText) {
      el.decisionText.classList.toggle("is-fail", !passed);
      el.decisionText.textContent = passed ? "APPROVED" : "REJECTED";
    }
    if (el.btnSettleApprove) el.btnSettleApprove.disabled = !passed;
  };

  el.sliderDescMatch.addEventListener("input", updateEvaluator);
  el.sliderSerialMatch.addEventListener("input", updateEvaluator);
  el.sliderPhotoMatch.addEventListener("input", updateEvaluator);

  if (el.btnSettleApprove) el.btnSettleApprove.addEventListener("click", () => handleSettleClaim("APPROVED"));
  if (el.btnSettleReject) el.btnSettleReject.addEventListener("click", () => handleSettleClaim("REJECTED"));

  updateEvaluator();
}

// Search & Filter listeners
function setupSearchAndFilters() {
  if (!el.searchInventory) return;

  const urlParams = new URLSearchParams(window.location.search);
  const searchParam = urlParams.get("search");
  if (searchParam) el.searchInventory.value = searchParam;

  const filterHandler = () => renderInventoryCards();
  el.searchInventory.addEventListener("input", filterHandler);
  if (el.filterType) el.filterType.addEventListener("change", filterHandler);
  if (el.filterStatus) el.filterStatus.addEventListener("change", filterHandler);
  if (el.filterCategory) el.filterCategory.addEventListener("change", filterHandler);
  if (el.btnRefreshInventory) {
    el.btnRefreshInventory.addEventListener("click", () => {
      loadAllData();
      showToast("Directory refreshed from database", "info");
    });
  }
}

// Dedicated Item Detail Page Setup
async function setupItemDetail() {
  const container = document.getElementById("item-detail-container");
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const itemId = params.get("id");
  if (!itemId) {
    container.innerHTML = `
      <div class="empty-state">
        <h4>No Item Specified</h4>
        <p>Please select an item from the <a href="items.html" style="color: var(--accent-text);">Property Directory</a>.</p>
      </div>
    `;
    return;
  }

  try {
    const res = await fetch(`/api/items/${itemId}`);
    if (!res.ok) throw new Error(`Item #${itemId} not found`);
    const data = await res.json();
    renderItemDetailPage(data.item);
  } catch (err) {
    const item = state.items.find(i => String(i.item_id) === String(itemId)) || OFFLINE_SEED_ITEMS.find(i => String(i.item_id) === String(itemId));
    if (item) {
      renderItemDetailPage(item);
    } else {
      container.innerHTML = `
        <div class="empty-state">
          <h4>Item #${escapeHtml(itemId)} Not Found</h4>
          <p>The requested property record could not be found or has been purged.</p>
          <a href="items.html" class="btn btn-secondary btn-sm" style="margin-top: 14px; display: inline-block;">Return to Directory</a>
        </div>
      `;
    }
  }
}

function renderItemDetailPage(item) {
  const container = document.getElementById("item-detail-container");
  if (!container) return;

  const isFound = item.item_type === "FOUND";
  const status = statusDisplay(item.status);
  const isHeld = Boolean(item.locker_code) && item.status !== "VERIFIED_RETURNED";
  const valFormatted = `₹${(parseFloat(item.reward_or_value) || 0).toLocaleString('en-IN')}`;
  const claims = item.claims || [];
  const isAdmin = state.userRole === "admin";

  container.innerHTML = `
    <div class="item-detail-hero">
      <div class="item-detail-hero-left">
        <div class="item-detail-badges">
          <span class="tag ${isFound ? 'tag-found' : 'tag-lost'}">${isFound ? 'Found Property' : 'Lost Property'}</span>
          <span class="tag ${status.cls}">${escapeHtml(status.label)}</span>
          <span class="tag tag-neutral">${escapeHtml(item.category)}</span>
          <span class="item-id-pill">Record #${item.item_id}</span>
        </div>
        <h1 class="item-detail-title">${escapeHtml(item.title)}</h1>
        <div class="item-detail-meta">
          <span>Reported: ${escapeHtml(item.reported_date || 'N/A')}</span>
          ${item.updated_at ? `<span>&bull; Last Activity: ${escapeHtml(item.updated_at)}</span>` : ''}
        </div>
      </div>

      <div class="item-detail-actions">
        ${isFound && item.status !== 'VERIFIED_RETURNED' ? `
          <button class="btn btn-primary" onclick="initiateClaimForItem(${item.item_id})">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#i-claim"/></svg>
            File Claim Ticket
          </button>
        ` : ''}

        ${isAdmin ? `
          <button class="btn btn-secondary" onclick="cycleStatus(${item.item_id})">
            Advance Status
          </button>
          <button class="btn btn-danger" onclick="deleteItemRecord(${item.item_id})" title="Delete record" aria-label="Delete">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#i-trash"/></svg>
            Delete
          </button>
        ` : ''}
      </div>
    </div>

    <div class="item-detail-grid">
      <!-- Left Column: Specs & Description -->
      <div>
        <div class="detail-card">
          <h3 class="detail-card-title">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#i-tag"/></svg>
            Property Description & Specifications
          </h3>
          <div class="detail-kv-grid">
            <div class="detail-kv-item">
              <span class="detail-kv-label">Category</span>
              <span class="detail-kv-val">${escapeHtml(item.category)}</span>
            </div>
            <div class="detail-kv-item">
              <span class="detail-kv-label">Location ${isFound ? 'Found' : 'Lost'}</span>
              <span class="detail-kv-val">${escapeHtml(item.location)}</span>
            </div>
            <div class="detail-kv-item">
              <span class="detail-kv-label">Declared Valuation</span>
              <span class="detail-kv-val is-money">${valFormatted}</span>
            </div>
            <div class="detail-kv-item">
              <span class="detail-kv-label">Current Status</span>
              <span class="detail-kv-val">${escapeHtml(status.label)}</span>
            </div>
          </div>

          <div style="margin-top: 20px;">
            <span class="detail-kv-label">Distinct Characteristics & Notes</span>
            <div class="detail-desc-box">${escapeHtml(item.description)}</div>
          </div>
        </div>

        <div class="detail-card">
          <h3 class="detail-card-title">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#i-brand"/></svg>
            Reporter Information
          </h3>
          <div class="detail-kv-grid">
            <div class="detail-kv-item">
              <span class="detail-kv-label">Reported By</span>
              <span class="detail-kv-val">${escapeHtml(item.reporter_name)}</span>
            </div>
            <div class="detail-kv-item">
              <span class="detail-kv-label">Campus Contact</span>
              <span class="detail-kv-val">${escapeHtml(item.reporter_contact)}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Custody & Claims -->
      <div>
        <div class="detail-card">
          <h3 class="detail-card-title">
            <svg class="icon icon-sm" aria-hidden="true"><use href="#i-locker"/></svg>
            Campus Storage & Custody
          </h3>
          ${item.locker_code ? `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
              <span class="locker-plate ${isHeld ? '' : 'is-released'}">${escapeHtml(lockerNumber(item.locker_code))}</span>
              <span class="tag ${isHeld ? 'tag-custody' : 'tag-returned'}">
                ${isHeld ? 'In Secure Custody' : 'Discharged'}
              </span>
            </div>
            <div class="detail-kv-grid">
              <div class="detail-kv-item">
                <span class="detail-kv-label">Custody Start</span>
                <span class="detail-kv-val">${escapeHtml(item.custody_start_date || 'N/A')}</span>
              </div>
              <div class="detail-kv-item">
                <span class="detail-kv-label">Discharge Date</span>
                <span class="detail-kv-val">${escapeHtml(item.release_date || 'Currently Active')}</span>
              </div>
            </div>
            <p style="font-size: var(--fs-xs); color: var(--text-2); margin-top: 14px; background: var(--bg); padding: 12px; border-radius: var(--r-control); line-height: 1.5;">
              ${escapeHtml(item.locker_remarks || 'Stored safely at Campus Lost Property Custody Office. Zero fee campus service.')}
            </p>
          ` : `
            <p style="color: var(--text-2); font-size: var(--fs-sm);">
              ${isFound ? 'No custody locker allocated.' : 'No storage assigned (Lost property search report).'}
            </p>
          `}
        </div>

        <div class="detail-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <h3 class="detail-card-title" style="margin-bottom: 0; border-bottom: none; padding-bottom: 0;">
              <svg class="icon icon-sm" aria-hidden="true"><use href="#i-claim"/></svg>
              Ownership Claims (${claims.length})
            </h3>
            ${isFound && item.status !== 'VERIFIED_RETURNED' ? `
              <button class="btn btn-secondary btn-sm" onclick="initiateClaimForItem(${item.item_id})">
                + File Claim
              </button>
            ` : ''}
          </div>

          ${claims.length > 0 ? `
            <div class="detail-claims-list">
              ${claims.map(c => `
                <div class="detail-claim-ticket">
                  <div class="detail-claim-header">
                    <strong>Claim #${c.claim_id}: ${escapeHtml(c.claimant_name)}</strong>
                    <span class="tag ${c.claim_status === 'APPROVED' ? 'tag-found' : c.claim_status === 'REJECTED' ? 'tag-lost' : 'tag-pending'}">
                      ${escapeHtml(c.claim_status)}
                    </span>
                  </div>
                  <div style="font-size: var(--fs-xs); color: var(--text-2);">
                    Contact: ${escapeHtml(c.claimant_contact)} | Score: ${c.confidence_score}%
                  </div>
                  <p style="font-size: var(--fs-xs); color: var(--text-3); font-style: italic; margin-top: 4px;">
                    "${escapeHtml(c.proof_description)}"
                  </p>
                </div>
              `).join('')}
            </div>
          ` : `
            <p style="color: var(--text-2); font-size: var(--fs-sm);">
              No claims submitted for this item yet.
            </p>
            ${isFound && item.status !== 'VERIFIED_RETURNED' ? `
              <button class="btn btn-primary btn-sm btn-block" style="margin-top: 14px;" onclick="initiateClaimForItem(${item.item_id})">
                Claim this Belonging
              </button>
            ` : ''}
          `}
        </div>
      </div>
    </div>
  `;
}

// ==============================================================================
// DATA FETCHING & SYNCHRONIZATION
// ==============================================================================

async function loadAllData() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error("API not available");

    const statusData = await res.json();
    state.isLiveApi = true;
    if (el.dbEngineLabel) {
      el.dbEngineLabel.textContent = `${statusData.db_type} Connected`;
      el.dbEngineLabel.parentElement.classList.remove("is-local");
    }

    const itemsRes = await fetch("/api/items");
    const itemsData = await itemsRes.json();
    state.items = itemsData.items || [];

    const claimsRes = await fetch("/api/claims");
    const claimsData = await claimsRes.json();
    state.claims = claimsData.claims || [];

    const lockersRes = await fetch("/api/lockers");
    const lockersData = await lockersRes.json();
    state.lockers = lockersData.lockers || [];

    const auditRes = await fetch("/api/audit");
    const auditData = await auditRes.json();
    state.audit = auditData.history || [];

    const analyticsRes = await fetch("/api/analytics");
    state.analytics = await analyticsRes.json();

  } catch (err) {
    state.isLiveApi = false;
    if (el.dbEngineLabel) {
      el.dbEngineLabel.textContent = "Local Offline Engine";
      el.dbEngineLabel.parentElement.classList.add("is-local");
    }

    if (state.items.length === 0) {
      state.items = [...OFFLINE_SEED_ITEMS];
      state.claims = [...OFFLINE_SEED_CLAIMS];
      generateLocalLockersAndAudit();
    }
  }

  updateMetrics();
  renderInventoryCards();
  renderClaimsQueue();
  renderLockersGrid();
  renderAuditTimeline();
  renderCategoryAnalytics();
}

function generateLocalLockersAndAudit() {
  state.lockers = [
    { locker_id: 1, locker_code: "LOCKER-A101", item_id: 1, item_title: "MacBook Pro 14 M2 Space Gray", category: "Electronics", status: "IN_CUSTODY", custody_start_date: "2026-09-02", release_date: null, is_released: false, days_held: 40, remarks: "Safely secured in Library 1st floor locker" },
    { locker_id: 2, locker_code: "LOCKER-B204", item_id: 2, item_title: "Leather Bifold Wallet (Brown)", category: "Keys/Wallets", status: "IN_CUSTODY", custody_start_date: "2026-09-08", release_date: null, is_released: false, days_held: 34, remarks: "Safely held in Cafeteria security desk locker" },
    { locker_id: 3, locker_code: "LOCKER-C301", item_id: 4, item_title: "Campus ID Card & Bus Pass", category: "Documents/Cards", status: "VERIFIED_RETURNED", custody_start_date: "2026-09-19", release_date: "2026-09-25", is_released: true, days_held: 6, remarks: "Claim verified and handed over to student" },
    { locker_id: 4, locker_code: "LOCKER-A102", item_id: 5, item_title: "Blue Hydro Flask Water Bottle", category: "Clothing/Apparel", status: "IN_CUSTODY", custody_start_date: "2026-09-22", release_date: null, is_released: false, days_held: 20, remarks: "Stored in Central Library safe locker" }
  ];

  state.audit = [
    { action_id: 1, item_id: 4, action_type: "CLAIM_VERIFIED_AND_RELEASED", snapshot_before: { status: "CLAIM_PENDING", claim_id: 4 }, snapshot_after: { status: "VERIFIED_RETURNED", score: 98.5 }, performed_at: "2026-09-25 10:00:00" },
    { action_id: 2, item_id: 5, action_type: "INSERT", snapshot_before: null, snapshot_after: { title: "Blue Hydro Flask", status: "IN_CUSTODY" }, performed_at: "2026-09-22 15:30:00" },
    { action_id: 3, item_id: 3, action_type: "INSERT", snapshot_before: null, snapshot_after: { title: "Sony WH-1000XM5", status: "REPORTED" }, performed_at: "2026-09-14 16:20:00" }
  ];
}

// Metrics
function updateMetrics() {
  const totalItems = state.items.length;
  const inCustody = state.items.filter(i => i.status === "IN_CUSTODY").length;
  const pendingClaims = state.claims.filter(c => c.claim_status === "PENDING").length;
  const returnedCount = state.items.filter(i => i.status === "VERIFIED_RETURNED").length;

  if (el.kpiTotalItems) el.kpiTotalItems.textContent = totalItems;
  if (el.kpiInCustody) el.kpiInCustody.textContent = inCustody;
  if (el.kpiPendingClaims) el.kpiPendingClaims.textContent = pendingClaims;
  if (el.kpiReturnedCount) el.kpiReturnedCount.textContent = returnedCount;

  if (el.badgeItemsCount) el.badgeItemsCount.textContent = totalItems;
  if (el.badgeClaimsCount) el.badgeClaimsCount.textContent = pendingClaims;
  if (el.badgeLockersCount) el.badgeLockersCount.textContent = `${inCustody} Active Lockers`;
  if (el.badgeAuditCount) el.badgeAuditCount.textContent = `${state.audit.length} Actions Logged`;
  if (el.stackCountTag) el.stackCountTag.textContent = `Depth: ${state.audit.length}`;
}

const STATUS_DISPLAY = {
  IN_CUSTODY: { label: "In custody", cls: "tag-custody" },
  CLAIM_PENDING: { label: "Claim pending", cls: "tag-pending" },
  VERIFIED_RETURNED: { label: "Returned to owner", cls: "tag-returned" },
  REPORTED: { label: "Reported", cls: "tag-reported" }
};

function statusDisplay(status) {
  return STATUS_DISPLAY[status] || { label: status, cls: "tag-neutral" };
}

function lockerNumber(code) {
  return String(code).replace(/^LOCKER-/, "");
}

// Render Inventory Cards
function renderInventoryCards() {
  if (!el.itemsContainer) return;

  const isIndexPage = window.location.pathname.endsWith("index.html") || window.location.pathname === "/" || window.location.pathname === "";
  const query = el.searchInventory ? el.searchInventory.value.trim().toLowerCase() : "";
  const typeFilter = el.filterType ? el.filterType.value : "";
  const statusFilter = el.filterStatus ? el.filterStatus.value : "";
  const catFilter = el.filterCategory ? el.filterCategory.value : "";

  let filtered = state.items.filter(item => {
    if (typeFilter && item.item_type !== typeFilter) return false;
    if (statusFilter && item.status !== statusFilter) return false;
    if (catFilter && item.category !== catFilter) return false;
    if (query) {
      const matchTitle = (item.title || "").toLowerCase().includes(query);
      const matchDesc = (item.description || "").toLowerCase().includes(query);
      const matchLoc = (item.location || "").toLowerCase().includes(query);
      if (!matchTitle && !matchDesc && !matchLoc) return false;
    }
    return true;
  });

  // On index dashboard, display the most recent 6 items to keep the page clean and uncongested
  if (isIndexPage && filtered.length > 6) {
    filtered = filtered.slice(0, 6);
  }

  if (filtered.length === 0) {
    el.itemsContainer.innerHTML = `
      <div class="empty-state">
        <h4>No matching items</h4>
        <p>Clear the search filter or register a new property report.</p>
      </div>
    `;
    return;
  }

  el.itemsContainer.innerHTML = filtered.map(item => {
    const isFound = item.item_type === "FOUND";
    const status = statusDisplay(item.status);
    const isHeld = Boolean(item.locker_code) && item.status !== "VERIFIED_RETURNED";
    const valFormatted = `₹${(parseFloat(item.reward_or_value) || 0).toLocaleString('en-IN')}`;
    const lockerPlate = item.locker_code
      ? `<span class="locker-plate ${isHeld ? '' : 'is-released'}" title="${escapeHtml(item.locker_code)}">${escapeHtml(lockerNumber(item.locker_code))}</span>`
      : `<span class="locker-plate is-none">${isFound ? 'No locker' : 'Lost item'}</span>`;

    return `
      <article class="item-card ${isHeld ? 'is-held' : ''}" data-id="${item.item_id}" onclick="window.location.href='item.html?id=${item.item_id}'" style="cursor: pointer;">
        <span class="tag-hole" aria-hidden="true"></span>
        <div class="item-card-header">
          <div class="item-badge-group">
            <span class="tag ${isFound ? 'tag-found' : 'tag-lost'}">${isFound ? 'Found' : 'Lost'}</span>
            <span class="tag ${status.cls}">${escapeHtml(status.label)}</span>
            <span class="tag tag-neutral">${escapeHtml(item.category)}</span>
          </div>
          <span class="item-id-pill">#${item.item_id}</span>
        </div>

        ${lockerPlate}
        <h3 class="item-title">
          <a href="item.html?id=${item.item_id}" onclick="event.stopPropagation();" style="color: inherit; text-decoration: none;">
            ${escapeHtml(item.title)}
          </a>
        </h3>
        <p class="item-desc">${escapeHtml(item.description)}</p>

        <div class="item-meta-row">
          <div class="meta-item">
            <span class="meta-label">Location</span>
            <span class="meta-val" title="${escapeHtml(item.location)}">${escapeHtml(item.location)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Reported by</span>
            <span class="meta-val" title="${escapeHtml(item.reporter_name)}">${escapeHtml(item.reporter_name)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Valuation</span>
            <span class="meta-val is-money">${valFormatted}</span>
          </div>
        </div>

        <div class="item-actions">
          <a href="item.html?id=${item.item_id}" class="btn btn-secondary btn-sm" onclick="event.stopPropagation();" style="text-decoration: none;">
            View Details &rarr;
          </a>

          <div class="item-actions-group">
            ${isFound && item.status !== 'VERIFIED_RETURNED' ? `
              <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); initiateClaimForItem(${item.item_id})">
                File Claim
              </button>
            ` : `
              <span class="item-date">${item.reported_date ? item.reported_date.split(' ')[0] : ''}</span>
            `}
          </div>
        </div>
      </article>
    `;
  }).join("");
}

// Claims Queue
function renderClaimsQueue() {
  if (!el.queueItemsContainer) return;

  const pendingClaims = state.claims.filter(c => c.claim_status === "PENDING");

  if (pendingClaims.length === 0) {
    el.queueItemsContainer.innerHTML = `
      <div class="empty-state">
        <h4>No claims pending review</h4>
        <p>All verification requests are cleared.</p>
      </div>
    `;
    if (el.selectedClaimTag) el.selectedClaimTag.textContent = "All Claims Reviewed";
    return;
  }

  if (!state.selectedClaim || !pendingClaims.some(c => c.claim_id === state.selectedClaim.claim_id)) {
    state.selectedClaim = pendingClaims[0];
  }

  if (el.selectedClaimTag) {
    el.selectedClaimTag.textContent = `Claim #${state.selectedClaim.claim_id}`;
  }

  el.queueItemsContainer.innerHTML = pendingClaims.map((claim, index) => {
    const isSelected = state.selectedClaim && state.selectedClaim.claim_id === claim.claim_id;
    return `
      <div class="queue-ticket ${isSelected ? 'active' : ''}" onclick="selectClaim(${claim.claim_id})">
        <span class="queue-pos-badge">Pending Review #${index + 1}</span>
        <h4 class="ticket-title">
          Claim #${claim.claim_id}: ${escapeHtml(claim.item_title || 'Item #' + claim.item_id)}
        </h4>
        <div class="ticket-claimant">
          Claimant: <strong>${escapeHtml(claim.claimant_name)}</strong> (${escapeHtml(claim.claimant_contact)})
        </div>
        <p class="ticket-proof">${escapeHtml(claim.proof_description)}</p>
      </div>
    `;
  }).join("");
}

function selectClaim(claimId) {
  state.selectedClaim = state.claims.find(c => c.claim_id === claimId);
  renderClaimsQueue();
}

// Lockers Grid
function renderLockersGrid() {
  if (!el.lockersContainer) return;

  if (state.lockers.length === 0) {
    el.lockersContainer.innerHTML = `
      <div class="empty-state">
        <h4>No storage lockers active</h4>
        <p>Lockers are allocated when found items are checked in.</p>
      </div>
    `;
    return;
  }

  el.lockersContainer.innerHTML = state.lockers.map(l => {
    const isOccupied = !l.release_date;
    return `
      <div class="locker-card ${isOccupied ? 'occupied' : 'released'}">
        <span class="tag-hole" aria-hidden="true"></span>
        <div class="locker-code-tag">
          <span class="locker-plate" title="${escapeHtml(l.locker_code)}">${escapeHtml(lockerNumber(l.locker_code))}</span>
          <span class="tag ${isOccupied ? 'tag-custody' : 'tag-returned'}">
            ${isOccupied ? 'In custody' : 'Released'}
          </span>
        </div>
        <h4 class="locker-title">
          ${escapeHtml(l.item_title || 'Stored Item #' + l.item_id)}
        </h4>
        <div class="locker-dates">
          Custody start: ${escapeHtml(l.custody_start_date || 'N/A')}
          ${l.release_date ? `<br>Discharged: ${escapeHtml(l.release_date)}` : ''}
        </div>
        <div class="locker-foot">
          <span class="locker-days-count">${l.days_held} days held</span>
          <span class="locker-fee">Zero fee campus service</span>
        </div>
      </div>
    `;
  }).join("");
}

// Audit Timeline
function renderAuditTimeline() {
  if (!el.auditTimelineContainer) return;

  if (state.audit.length === 0) {
    el.auditTimelineContainer.innerHTML = `
      <div class="empty-state">
        <h4>No actions recorded</h4>
        <p>Item registrations and status changes appear here.</p>
      </div>
    `;
    return;
  }

  el.auditTimelineContainer.innerHTML = state.audit.map(a => {
    const afterStr = typeof a.snapshot_after === 'object' ? JSON.stringify(a.snapshot_after, null, 2) : a.snapshot_after;
    return `
      <div class="timeline-item">
        <div class="timeline-header">
          <span class="timeline-type">${escapeHtml(a.action_type)}</span>
          <span class="timeline-time">${escapeHtml(a.performed_at || '')}</span>
        </div>
        <div class="timeline-target">
          Target: Item ID #${a.item_id || 'Global'}
        </div>
        ${afterStr ? `<pre class="json-snapshot">Snapshot: ${escapeHtml(afterStr)}</pre>` : ''}
      </div>
    `;
  }).join("");
}

// Category Analytics
function renderCategoryAnalytics() {
  if (!el.categoryAnalyticsTbody) return;

  const cats = (state.analytics && state.analytics.categories) ? state.analytics.categories : [
    { category_name: "Electronics", total_items: 3, found_count: 1, lost_count: 2, total_declared_value: 154500.0 },
    { category_name: "Keys/Wallets", total_items: 1, found_count: 1, lost_count: 0, total_declared_value: 2500.0 },
    { category_name: "Documents/Cards", total_items: 1, found_count: 1, lost_count: 0, total_declared_value: 500.0 },
    { category_name: "Clothing/Apparel", total_items: 1, found_count: 1, lost_count: 0, total_declared_value: 1800.0 }
  ];

  el.categoryAnalyticsTbody.innerHTML = cats.map(c => `
    <tr>
      <td class="cell-strong">${escapeHtml(c.category_name)}</td>
      <td>${c.total_items}</td>
      <td><span class="tag tag-found">${c.found_count}</span></td>
      <td><span class="tag tag-lost">${c.lost_count}</span></td>
      <td class="cell-money">₹${(parseFloat(c.total_declared_value) || 0).toLocaleString('en-IN')}</td>
    </tr>
  `).join("");
}

// Form Handlers
async function handleReportItemSubmit(e) {
  e.preventDefault();

  const newItem = {
    title: document.getElementById("item-title-input").value.trim(),
    category: document.getElementById("item-category-input").value,
    item_type: document.getElementById("item-type-input").value,
    location: document.getElementById("item-location-input").value.trim(),
    description: document.getElementById("item-desc-input").value.trim(),
    reward_or_value: parseFloat(document.getElementById("item-val-input").value) || 0,
    reporter_name: document.getElementById("item-reporter-name").value.trim(),
    reporter_contact: document.getElementById("item-reporter-contact").value.trim()
  };

  try {
    if (state.isLiveApi) {
      const res = await fetch("/api/items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newItem)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to create item");
      showToast(`Item #${data.item.item_id} registered successfully!`, "success");
    } else {
      newItem.item_id = state.items.length + 1;
      newItem.status = newItem.item_type === "FOUND" ? "IN_CUSTODY" : "REPORTED";
      newItem.reported_date = new Date().toISOString().replace('T', ' ').substring(0, 19);
      newItem.locker_code = newItem.item_type === "FOUND" ? `LOCKER-X${100 + newItem.item_id}` : null;
      state.items.unshift(newItem);
      showToast(`Item #${newItem.item_id} registered successfully!`, "success");
    }

    closeModal(el.modalReportItem);
    el.formReportItem.reset();
    await loadAllData();

  } catch (err) {
    showToast(err.message, "error");
  }
}

function initiateClaimForItem(itemId) {
  populateClaimSelectDropdown();
  if (el.claimItemSelect) el.claimItemSelect.value = String(itemId);
  openModal(el.modalSubmitClaim);
}

function populateClaimSelectDropdown() {
  if (!el.claimItemSelect) return;
  const foundItems = state.items.filter(i => i.item_type === "FOUND" && i.status !== "VERIFIED_RETURNED");
  if (foundItems.length === 0) {
    el.claimItemSelect.innerHTML = `<option value="">No found items currently in custody</option>`;
    return;
  }
  el.claimItemSelect.innerHTML = foundItems.map(i => `
    <option value="${i.item_id}">#${i.item_id} - ${escapeHtml(i.title)} (${escapeHtml(i.location)})</option>
  `).join("");
}

async function handleSubmitClaimSubmit(e) {
  e.preventDefault();

  const targetItemId = parseInt(el.claimItemSelect.value);
  if (!targetItemId) {
    showToast("Please select a target item.", "error");
    return;
  }

  const newClaim = {
    item_id: targetItemId,
    claimant_name: document.getElementById("claimant-name-input").value.trim(),
    claimant_contact: document.getElementById("claimant-contact-input").value.trim(),
    proof_description: document.getElementById("claim-proof-input").value.trim()
  };

  try {
    if (state.isLiveApi) {
      const res = await fetch("/api/claims", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newClaim)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to submit claim");
      showToast(`Claim #${data.claim.claim_id} submitted for verification!`, "success");
    } else {
      const targetItem = state.items.find(i => i.item_id === targetItemId);
      newClaim.claim_id = state.claims.length + 1;
      newClaim.confidence_score = 0;
      newClaim.claim_status = "PENDING";
      newClaim.submitted_at = new Date().toISOString().replace('T', ' ').substring(0, 19);
      newClaim.item_title = targetItem ? targetItem.title : `Item #${targetItemId}`;
      newClaim.item_category = targetItem ? targetItem.category : "General";
      newClaim.locker_code = targetItem ? targetItem.locker_code : null;

      state.claims.push(newClaim);
      if (targetItem) targetItem.status = "CLAIM_PENDING";
      showToast(`Claim #${newClaim.claim_id} submitted for verification!`, "success");
    }

    closeModal(el.modalSubmitClaim);
    el.formSubmitClaim.reset();
    await loadAllData();

  } catch (err) {
    showToast(err.message, "error");
  }
}

async function handleSettleClaim(decision) {
  if (!state.selectedClaim) {
    showToast("No claim selected for review.", "error");
    return;
  }

  const claimId = state.selectedClaim.claim_id;
  const itemId = state.selectedClaim.item_id;
  const score = (rpnVariables.desc_match * 0.4) + (rpnVariables.serial_match * 0.4) + (rpnVariables.photo_match * 0.2);

  try {
    if (state.isLiveApi) {
      const res = await fetch("/api/claims/settle-atomic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          claim_id: claimId,
          item_id: itemId,
          confidence_score: score,
          decision: decision
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Transaction failed");
      showToast(`Claim #${claimId} ${decision} successfully`, "success");
    } else {
      const claim = state.claims.find(c => c.claim_id === claimId);
      const item = state.items.find(i => i.item_id === itemId);
      const locker = state.lockers.find(l => l.item_id === itemId && !l.release_date);

      if (claim) {
        claim.claim_status = decision;
        claim.confidence_score = score;
      }
      if (decision === "APPROVED") {
        if (item) item.status = "VERIFIED_RETURNED";
        if (locker) {
          locker.release_date = new Date().toISOString().split('T')[0];
          locker.is_released = true;
          locker.remarks = "Verified and returned to student";
        }
      } else {
        if (item) item.status = "IN_CUSTODY";
      }

      state.audit.unshift({
        action_id: state.audit.length + 1,
        item_id: itemId,
        action_type: decision === "APPROVED" ? "CLAIM_VERIFIED_AND_RELEASED" : "CLAIM_REJECTED",
        snapshot_before: { status: "CLAIM_PENDING", claim_id: claimId },
        snapshot_after: { status: decision === "APPROVED" ? "VERIFIED_RETURNED" : "IN_CUSTODY", score: score },
        performed_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
      });

      showToast(`Claim #${claimId} ${decision} successfully`, "success");
    }

    state.selectedClaim = null;
    await loadAllData();

  } catch (err) {
    showToast(err.message, "error");
  }
}

async function handleUndoAction() {
  try {
    if (state.isLiveApi) {
      const res = await fetch("/api/audit/undo", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Undo failed");
      showToast(`↩ ${data.message}`, "success");
    } else {
      if (state.audit.length === 0) {
        showToast("No actions available to rollback.", "error");
        return;
      }
      const popped = state.audit.shift();
      showToast(`↩ Undid ${popped.action_type} for Item #${popped.item_id}`, "success");
    }
    await loadAllData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function cycleStatus(itemId) {
  const item = state.items.find(i => i.item_id === itemId);
  if (!item) return;

  const order = ["REPORTED", "IN_CUSTODY", "CLAIM_PENDING", "VERIFIED_RETURNED"];
  const currIdx = order.indexOf(item.status);
  const nextStatus = order[(currIdx + 1) % order.length];

  try {
    if (state.isLiveApi) {
      await fetch(`/api/items/${itemId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus })
      });
    } else {
      item.status = nextStatus;
    }
    showToast(`Status updated to ${nextStatus}`, "success");
    await loadAllData();
    if (document.getElementById("item-detail-container")) {
      setupItemDetail();
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteItemRecord(itemId) {
  if (!confirm(`Are you sure you want to permanently delete record #${itemId}?`)) {
    return;
  }

  try {
    if (state.isLiveApi) {
      const res = await fetch(`/api/items/${itemId}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Delete failed");
      showToast(`Record #${itemId} deleted.`, "info");
    } else {
      state.items = state.items.filter(i => i.item_id !== itemId);
      showToast(`Record #${itemId} deleted.`, "info");
    }

    if (document.getElementById("item-detail-container")) {
      window.location.href = "items.html";
    } else {
      await loadAllData();
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ==============================================================================
// UTILITY FUNCTIONS
// ==============================================================================

function showToast(message, type = "info") {
  let toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";
    toastContainer.className = "toast-container";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✔' : type === 'error' ? '✖' : 'ℹ'}</span>
    <span>${escapeHtml(message)}</span>
  `;
  while (toastContainer.children.length >= 2) {
    toastContainer.firstElementChild.remove();
  }
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
