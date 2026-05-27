/**
 * BHIV REGISTRY Explorer SPA
 * Core Application Controller (ES6 Module)
 */

const API_BASE = "http://localhost:8000/api/v1";

const TRUST_TRANSITIONS = {
    "UNVERIFIED": [
        { level: "PROVISIONAL", label: "Audit & Provisional", icon: "fa-shield-halved", class: "btn-outline" },
        { level: "QUARANTINE", label: "Quarantine Dataset", icon: "fa-biohazard", class: "btn-primary" }
    ],
    "PROVISIONAL": [
        { level: "TRUSTED", label: "Promote to Trusted", icon: "fa-square-check", class: "btn-outline" },
        { level: "UNVERIFIED", label: "Demote to Unverified", icon: "fa-circle-exclamation", class: "btn-outline" },
        { level: "QUARANTINE", label: "Quarantine Dataset", icon: "fa-biohazard", class: "btn-primary" }
    ],
    "TRUSTED": [
        { level: "VERIFIED", label: "Formally Verify", icon: "fa-check-double", class: "btn-outline" },
        { level: "PROVISIONAL", label: "Demote to Provisional", icon: "fa-shield-halved", class: "btn-outline" },
        { level: "QUARANTINE", label: "Quarantine Dataset", icon: "fa-biohazard", class: "btn-primary" }
    ],
    "VERIFIED": [
        { level: "TRUSTED", label: "Demote to Trusted", icon: "fa-square-check", class: "btn-outline" },
        { level: "QUARANTINE", label: "Quarantine Dataset", icon: "fa-biohazard", class: "btn-primary" }
    ],
    "QUARANTINE": [
        { level: "UNVERIFIED", label: "Restore to Unverified", icon: "fa-arrow-rotate-left", class: "btn-outline" }
    ]
};

// Global App State
const state = {
    currentView: "dashboard",
    datasets: [],
    filteredDatasets: [],
    onboardingQueue: [],
    selectedDataset: null,
    selectedSchemaDatasetId: null,
    selectedSchemaVersion: null,
    selectedLineageDatasetId: null,
    filters: {
        domain_primary: "",
        trust_level: "",
        replay_compatibility: "",
        simulation_compatibility: "",
        search_text: ""
    }
};

// ==========================================================================
// 1. INITS & ROUTING
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
    initViewRouter();
    await checkApiConnection();
    await loadInitialData();
    initEventListeners();
});

// Simple Hash Router
function initViewRouter() {
    const handleRoute = () => {
        const hash = window.location.hash || "#dashboard";
        const view = hash.replace("#", "");
        
        // Hide all views
        document.querySelectorAll(".viewport-section").forEach(sec => sec.classList.remove("active"));
        document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
        
        // Show active view
        const targetView = document.getElementById(`view-${view}`);
        const targetNav = document.getElementById(`nav-${view}`);
        
        if (targetView && targetNav) {
            targetView.classList.add("active");
            targetNav.classList.add("active");
            state.currentView = view;
            
            // View specific load triggers
            onViewChange(view);
        }
    };
    
    window.addEventListener("hashchange", handleRoute);
    handleRoute(); // Run initially
}

async function checkApiConnection() {
    const indicator = document.getElementById("api-status-indicator");
    const text = document.getElementById("api-status-text");
    try {
        const res = await fetch(`${API_BASE.replace('/api/v1', '')}/health`);
        if (res.ok) {
            indicator.className = "status-indicator online";
            text.textContent = "Backend Connected";
        } else {
            throw new Error();
        }
    } catch {
        indicator.className = "status-indicator offline";
        text.textContent = "Backend Offline";
        showToast("Cannot connect to FastAPI backend on port 8000.", "error");
    }
}

async function loadInitialData() {
    await fetchDashboardSummary();
    await fetchDatasets();
    await fetchOnboardingQueue();
}

function onViewChange(view) {
    if (view === "dashboard") {
        fetchDashboardSummary();
    } else if (view === "catalog") {
        renderCatalog();
    } else if (view === "schemas") {
        renderSchemaSelector();
    } else if (view === "lineage") {
        renderLineageSelector();
    } else if (view === "onboarding") {
        fetchOnboardingQueue();
    }
}

// ==========================================================================
// 2. EVENT LISTENERS
// ==========================================================================
function initEventListeners() {
    // Global search
    document.getElementById("global-search-input").addEventListener("input", (e) => {
        state.filters.search_text = e.target.value;
        if (state.currentView === "catalog") {
            applyClientFiltering();
        }
    });

    // Catalog filtering
    document.getElementById("btn-apply-filters").addEventListener("click", () => {
        state.filters.domain_primary = document.getElementById("filter-domain").value;
        state.filters.trust_level = document.getElementById("filter-trust").value;
        state.filters.replay_compatibility = document.getElementById("filter-replay").value;
        state.filters.simulation_compatibility = document.getElementById("filter-simulation").value;
        applyClientFiltering();
    });
    
    document.getElementById("btn-reset-filters").addEventListener("click", () => {
        document.getElementById("filter-domain").value = "";
        document.getElementById("filter-trust").value = "";
        document.getElementById("filter-replay").value = "";
        document.getElementById("filter-simulation").value = "";
        state.filters = {
            domain_primary: "",
            trust_level: "",
            replay_compatibility: "",
            simulation_compatibility: "",
            search_text: document.getElementById("global-search-input").value
        };
        applyClientFiltering();
    });

    // Run Provenance Audit
    document.getElementById("btn-run-provenance-audit").addEventListener("click", runProvenanceAudit);

    // Dataset details drawer closing
    document.getElementById("btn-close-drawer").addEventListener("click", toggleDrawer);
    document.getElementById("dataset-drawer-overlay").addEventListener("click", (e) => {
        if (e.target.id === "dataset-drawer-overlay") toggleDrawer();
    });

    // Schema Hub listeners
    document.getElementById("schema-dataset-search").addEventListener("input", (e) => {
        renderSchemaSelector(e.target.value);
    });
    document.getElementById("btn-create-schema-draft").addEventListener("click", openSchemaModal);
    document.getElementById("btn-close-schema-modal").addEventListener("click", closeSchemaModal);
    document.getElementById("btn-cancel-schema-modal").addEventListener("click", closeSchemaModal);
    document.getElementById("schema-draft-form").addEventListener("submit", handleCreateSchema);

    // Lineage Hub listeners
    document.getElementById("lineage-dataset-search").addEventListener("input", (e) => {
        renderLineageSelector(e.target.value);
    });
    document.getElementById("btn-add-relationship").addEventListener("click", openRelationshipModal);
    document.getElementById("btn-close-relationship-modal").addEventListener("click", closeRelationshipModal);
    document.getElementById("btn-cancel-relationship-modal").addEventListener("click", closeRelationshipModal);
    document.getElementById("relationship-form").addEventListener("submit", handleCreateRelationship);

    // Onboarding Submission
    document.getElementById("onboarding-submit-form").addEventListener("submit", handleOnboardingSubmit);
}

// ==========================================================================
// 3. API FETCH & DATA PROCESSING
// ==========================================================================
async function fetchDatasets() {
    try {
        const res = await fetch(`${API_BASE}/datasets/?page_size=100`);
        if (res.ok) {
            const data = await res.json();
            state.datasets = data.results;
            state.filteredDatasets = [...state.datasets];
        }
    } catch (err) {
        console.error("Error fetching datasets:", err);
    }
}

async function fetchDashboardSummary() {
    try {
        const res = await fetch(`${API_BASE}/discovery/summary`);
        if (res.ok) {
            const data = await res.json();
            
            document.getElementById("stat-total-datasets").textContent = data.total_datasets;
            document.getElementById("stat-trusted-datasets").textContent = 
                (data.by_trust_level.VERIFIED || 0) + (data.by_trust_level.TRUSTED || 0);
            document.getElementById("stat-replay-datasets").textContent = 
                (data.by_replay_compatibility.FULL || 0) + (data.by_replay_compatibility.PARTIAL || 0);
            document.getElementById("stat-quarantined-datasets").textContent = data.by_trust_level.QUARANTINE || 0;
            
            renderTrustDistribution(data.by_trust_level, data.total_datasets);
        }
    } catch (err) {
        console.error("Error loading summary:", err);
    }
}

async function fetchOnboardingQueue() {
    try {
        const res = await fetch(`${API_BASE}/onboarding/pending`);
        if (res.ok) {
            state.onboardingQueue = await res.json();
            
            const badge = document.getElementById("onboarding-pending-badge");
            if (state.onboardingQueue.length > 0) {
                badge.textContent = state.onboardingQueue.length;
                badge.style.display = "inline-flex";
            } else {
                badge.style.display = "none";
            }
            
            if (state.currentView === "onboarding") {
                renderOnboardingQueue();
            }
        }
    } catch (err) {
        console.error("Error fetching onboarding pending queue:", err);
    }
}

// Client filtering
function applyClientFiltering() {
    const s = state.filters;
    state.filteredDatasets = state.datasets.filter(ds => {
        const matchesSearch = s.search_text ? (
            ds.dataset_name.toLowerCase().includes(s.search_text.toLowerCase()) ||
            ds.canonical_id.toLowerCase().includes(s.search_text.toLowerCase()) ||
            ds.owner_name.toLowerCase().includes(s.search_text.toLowerCase()) ||
            (ds.description && ds.description.toLowerCase().includes(s.search_text.toLowerCase()))
        ) : true;
        
        const matchesDomain = s.domain_primary ? ds.domain_primary === s.domain_primary : true;
        const matchesTrust = s.trust_level ? ds.trust_level === s.trust_level : true;
        const matchesReplay = s.replay_compatibility ? ds.replay_compatibility === s.replay_compatibility : true;
        const matchesSim = s.simulation_compatibility ? ds.simulation_compatibility === s.simulation_compatibility : true;
        
        return matchesSearch && matchesDomain && matchesTrust && matchesReplay && matchesSim;
    });
    
    renderCatalog();
}

// ==========================================================================
// 4. RENDERING FUNCTIONS
// ==========================================================================

// Dashboard widgets
function renderTrustDistribution(distribution, total) {
    const list = document.getElementById("trust-distribution-list");
    list.innerHTML = "";
    
    const levels = ["VERIFIED", "TRUSTED", "PROVISIONAL", "UNVERIFIED", "QUARANTINE"];
    
    levels.forEach(level => {
        const count = distribution[level] || 0;
        const percent = total > 0 ? Math.round((count / total) * 100) : 0;
        
        const item = document.createElement("div");
        item.className = "distribution-item";
        item.innerHTML = `
            <div class="dist-meta">
                <span class="dist-label">${level}</span>
                <span class="dist-val">${count} (${percent}%)</span>
            </div>
            <div class="dist-bar-wrapper">
                <div class="dist-bar ${level.toLowerCase()}" style="width: ${percent}%"></div>
            </div>
        `;
        list.appendChild(item);
    });
}

// Catalog View
function renderCatalog() {
    const grid = document.getElementById("catalog-listings-grid");
    grid.innerHTML = "";
    
    document.getElementById("catalog-count-label").textContent = `Showing ${state.filteredDatasets.length} datasets`;
    
    if (state.filteredDatasets.length === 0) {
        grid.innerHTML = `
            <div class="panel-empty-state" style="grid-column: 1 / -1; padding: 64px 0;">
                <i class="fa-solid fa-database"></i>
                <p>No datasets match the selected filters.</p>
            </div>
        `;
        return;
    }
    
    state.filteredDatasets.forEach(ds => {
        const card = document.createElement("div");
        card.className = "dataset-card card";
        card.addEventListener("click", () => openDatasetDetails(ds.id));
        
        const tagsHtml = ds.domain_tags.map(t => `<span class="tag">${t}</span>`).join("");
        
        card.innerHTML = `
            <div class="dataset-card-header">
                <div>
                    <h4>${ds.dataset_name}</h4>
                    <span class="dataset-id-label">${ds.canonical_id}</span>
                </div>
                <span class="badge ${ds.trust_level.toLowerCase()}">${ds.trust_level}</span>
            </div>
            <p>${ds.description || "No description provided."}</p>
            <div class="dataset-tags">${tagsHtml}</div>
            <div class="dataset-card-footer">
                <div class="dataset-owner-info">
                    <span class="owner-team">${ds.owner_team || ds.owner_name}</span>
                    <span class="owner-system">${ds.source_system}</span>
                </div>
                <div class="dataset-compat-indicators">
                    <i class="fa-solid fa-rotate" title="Replay: ${ds.replay_compatibility}" style="color: ${getCompatColor(ds.replay_compatibility)}; margin-right: 8px;"></i>
                    <i class="fa-solid fa-microchip" title="Simulation: ${ds.simulation_compatibility}" style="color: ${getCompatColor(ds.simulation_compatibility)};"></i>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function getCompatColor(value) {
    if (value === "FULL" || value === "NATIVE" || value === "COMPATIBLE") return "var(--status-verified)";
    if (value === "PARTIAL" || value === "ADAPTABLE" || value === "CONDITIONAL") return "var(--status-provisional)";
    return "var(--text-muted)";
}

// Open details drawer
async function openDatasetDetails(id) {
    try {
        const res = await fetch(`${API_BASE}/datasets/${id}`);
        if (res.ok) {
            const ds = await res.json();
            
            // Get trust history & provenance
            const provRes = await fetch(`${API_BASE}/datasets/${id}/provenance`);
            const prov = provRes.ok ? await provRes.json() : [];
            
            const drawerContent = document.getElementById("dataset-drawer-content");
            
            const tagsHtml = ds.domain_tags.map(t => `<span class="tag">${t}</span>`).join("");
            
            let provListHtml = prov.map(pr => `
                <div class="prov-node">
                    <div class="prov-bullet"></div>
                    <div class="prov-content">
                        <div class="prov-header">
                            <span class="prov-type">${pr.event_type}</span>
                            <span class="prov-date">${new Date(pr.recorded_at).toLocaleDateString()}</span>
                        </div>
                        <p class="prov-notes">${pr.notes || ""}</p>
                        <span class="prov-system">${pr.source_system || "System"} • By ${pr.recorded_by}</span>
                    </div>
                </div>
            `).join("");
            
            if (prov.length === 0) {
                provListHtml = `<p style="color: var(--text-muted); font-size: 12px;">No provenance events recorded.</p>`;
            }
            
            // Dynamically render valid transition buttons
            const transitions = TRUST_TRANSITIONS[ds.trust_level] || [];
            let buttonsHtml = "";
            transitions.forEach(t => {
                buttonsHtml += `
                    <button class="btn ${t.class} btn-sm btn-block" id="btn-drawer-trust-${t.level.toLowerCase()}">
                        <i class="fa-solid ${t.icon}"></i> ${t.label}
                    </button>
                `;
            });

            drawerContent.innerHTML = `
                <div class="drawer-title-area">
                    <span class="badge ${ds.trust_level.toLowerCase()}" style="margin-bottom: 8px;">${ds.trust_level}</span>
                    <h3>${ds.dataset_name}</h3>
                    <span class="canonical-badge">${ds.canonical_id}</span>
                </div>
                
                <p style="color: var(--text-secondary); font-size: 13px;">${ds.description || "No description provided."}</p>
                <div class="dataset-tags">${tagsHtml}</div>
                
                <div>
                    <h4 class="drawer-section-title">Ownership & Identity</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Owner Name</span>
                            <span class="detail-value">${ds.owner_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Owner Team</span>
                            <span class="detail-value">${ds.owner_team || "-"}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Source System</span>
                            <span class="detail-value">${ds.source_system}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Registered At</span>
                            <span class="detail-value">${new Date(ds.registered_at).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h4 class="drawer-section-title">Ecosystem Compatibility</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Replay Compatibility</span>
                            <span class="detail-value" style="color: ${getCompatColor(ds.replay_compatibility)}">${ds.replay_compatibility}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Simulation Compatibility</span>
                            <span class="detail-value" style="color: ${getCompatColor(ds.simulation_compatibility)}">${ds.simulation_compatibility}</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h4 class="drawer-section-title">Provenance Event Chain</h4>
                    <div class="drawer-provenance-list">
                        ${provListHtml}
                    </div>
                </div>
                
                <div style="margin-top: 12px; display: flex; gap: 8px;">
                    ${buttonsHtml}
                </div>
            `;
            
            toggleDrawer(true);
            
            // Wire up event listeners
            transitions.forEach(t => {
                document.getElementById(`btn-drawer-trust-${t.level.toLowerCase()}`).addEventListener("click", () => handleTransitionTrust(ds.id, t.level));
            });
            
        }
    } catch (err) {
        showToast("Error loading dataset details.", "error");
        console.error(err);
    }
}

function toggleDrawer(open = false) {
    const overlay = document.getElementById("dataset-drawer-overlay");
    if (open) {
        overlay.classList.add("active");
    } else {
        overlay.classList.remove("active");
    }
}

// Transition trust level
async function handleTransitionTrust(datasetId, level) {
    try {
        let note = "Audit triggered from operator control UI.";
        if (level === "QUARANTINE") {
            note = prompt("Enter justification for Quarantining this dataset:") || "Quarantined due to operational boundaries review.";
        }
        
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/trust/transition`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                trust_level: level,
                verified_by: "Fullstack Operator",
                governance_notes: note
            })
        });
        
        if (res.ok) {
            showToast(`Dataset trust level successfully transitioned to ${level}!`, "success");
            toggleDrawer(false);
            await fetchDatasets();
            await fetchDashboardSummary();
            renderCatalog();
        } else {
            const err = await res.json();
            showToast(`Transition failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error updating trust level.", "error");
    }
}

// ==========================================================================
// 5. SCHEMA HUB HUB
// ==========================================================================
function renderSchemaSelector(filterQuery = "") {
    const list = document.getElementById("schema-datasets-list");
    list.innerHTML = "";
    
    const filtered = state.datasets.filter(ds => 
        ds.dataset_name.toLowerCase().includes(filterQuery.toLowerCase()) ||
        ds.canonical_id.toLowerCase().includes(filterQuery.toLowerCase())
    );
    
    filtered.forEach(ds => {
        const item = document.createElement("div");
        item.className = `schema-selector-item ${state.selectedSchemaDatasetId === ds.id ? 'active' : ''}`;
        item.innerHTML = `
            <div class="selector-item-name">${ds.dataset_name}</div>
            <div class="selector-item-meta">
                <span>${ds.canonical_id}</span>
                <span>v${ds.version}</span>
            </div>
        `;
        item.addEventListener("click", () => selectSchemaDataset(ds));
        list.appendChild(item);
    });
}

async function selectSchemaDataset(ds) {
    state.selectedSchemaDatasetId = ds.id;
    
    // Highlight item
    document.querySelectorAll(".schema-selector-item").forEach(item => item.classList.remove("active"));
    renderSchemaSelector(document.getElementById("schema-dataset-search").value);
    
    // Show content
    document.getElementById("schema-inspector-empty").style.display = "none";
    const content = document.getElementById("schema-inspector-content");
    content.style.display = "flex";
    
    document.getElementById("schema-dataset-title").textContent = ds.dataset_name;
    document.getElementById("schema-dataset-canonical-id").textContent = ds.canonical_id;
    
    await loadSchemaVersions(ds.id);
}

async function loadSchemaVersions(datasetId) {
    try {
        const res = await fetch(`${API_BASE}/schemas/dataset/${datasetId}`);
        if (res.ok) {
            const schemas = await res.json();
            const tabsContainer = document.getElementById("schema-versions-tabs");
            tabsContainer.innerHTML = "";
            
            if (schemas.length === 0) {
                tabsContainer.innerHTML = `<span style="color: var(--text-muted); padding: 8px 0; font-size:12px;">No schemas defined yet.</span>`;
                document.getElementById("schema-version-details").style.display = "none";
                return;
            }
            
            document.getElementById("schema-version-details").style.display = "flex";
            
            // Sort by version descending or simple order
            schemas.forEach((sch, idx) => {
                const tab = document.createElement("div");
                tab.className = `schema-tab ${idx === 0 ? 'active' : ''}`;
                tab.textContent = `v${sch.schema_version}`;
                tab.addEventListener("click", () => {
                    document.querySelectorAll(".schema-tab").forEach(t => t.classList.remove("active"));
                    tab.classList.add("active");
                    renderSchemaVersion(sch);
                });
                tabsContainer.appendChild(tab);
            });
            
            // Render first one initially
            renderSchemaVersion(schemas[0]);
        }
    } catch (err) {
        console.error(err);
        showToast("Error loading schemas.", "error");
    }
}

function renderSchemaVersion(schema) {
    document.getElementById("inspect-schema-status").textContent = schema.status;
    document.getElementById("inspect-schema-status").className = `badge ${schema.status.toLowerCase()}`;
    document.getElementById("inspect-schema-author").textContent = schema.created_by;
    document.getElementById("inspect-schema-date").textContent = new Date(schema.created_at).toLocaleDateString();
    
    const actionsBar = document.getElementById("schema-actions-bar");
    actionsBar.innerHTML = "";
    
    if (schema.status === "DRAFT") {
        const activateBtn = document.createElement("button");
        activateBtn.className = "btn btn-primary btn-sm";
        activateBtn.innerHTML = `<i class="fa-solid fa-check"></i> Activate Version`;
        activateBtn.addEventListener("click", () => handleSchemaAction(schema.id, "activate"));
        actionsBar.appendChild(activateBtn);
    } else if (schema.status === "ACTIVE") {
        const freezeBtn = document.createElement("button");
        freezeBtn.className = "btn btn-outline btn-sm";
        freezeBtn.innerHTML = `<i class="fa-solid fa-lock"></i> Freeze Schema`;
        freezeBtn.addEventListener("click", () => handleSchemaAction(schema.id, "freeze"));
        actionsBar.appendChild(freezeBtn);
    } else if (schema.status === "FROZEN") {
        actionsBar.innerHTML = `<span style="font-size: 11px; font-weight: 700; color: var(--status-verified);"><i class="fa-solid fa-circle-check"></i> IMMUTABLE: Schema version is frozen and ready for production replay!</span>`;
    }
    
    const tbody = document.getElementById("schema-fields-tbody");
    tbody.innerHTML = "";
    
    const fields = schema.field_definitions;
    fields.forEach(field => {
        const row = document.createElement("tr");
        const nameVal = field.field_name || field.name || "-";
        const typeVal = field.data_type || field.type || "-";
        row.innerHTML = `
            <td><strong>${nameVal}</strong></td>
            <td><code>${typeVal}</code></td>
            <td>${field.nullable ? "Yes" : "No"}</td>
            <td>${field.description || "-"}</td>
        `;
        tbody.appendChild(row);
    });
}

async function handleSchemaAction(schemaId, action) {
    try {
        const endpoint = action === "freeze" ? `${API_BASE}/schemas/${schemaId}/freeze` : `${API_BASE}/schemas/${schemaId}/activate`;
        const method = action === "freeze" ? "POST" : "PATCH";
        const res = await fetch(endpoint, { method });
        
        if (res.ok) {
            showToast(`Schema successfully ${action === "freeze" ? "frozen" : "activated"}!`, "success");
            await loadSchemaVersions(state.selectedSchemaDatasetId);
        } else {
            const err = await res.json();
            showToast(`Failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error updating schema version state.", "error");
    }
}

function openSchemaModal() {
    document.getElementById("schema-modal-overlay").classList.add("active");
    // Pre-populate with standard template if empty
    const fieldsText = document.getElementById("schema-fields-json");
    if (!fieldsText.value) {
        fieldsText.value = JSON.stringify([
            { "name": "timestamp", "type": "datetime", "nullable": false, "description": "UTC transaction timestamp" },
            { "name": "price", "type": "decimal", "nullable": false, "description": "Unit asset trade price" },
            { "name": "volume", "type": "integer", "nullable": false, "description": "Total traded asset units" }
        ], null, 2);
    }
}

function closeSchemaModal() {
    document.getElementById("schema-modal-overlay").classList.remove("active");
}

async function handleCreateSchema(e) {
    e.preventDefault();
    const version = document.getElementById("schema-version-input").value;
    const author = document.getElementById("schema-author-input").value;
    const notes = document.getElementById("schema-notes-input").value;
    const fieldsJsonStr = document.getElementById("schema-fields-json").value;
    
    try {
        const fields = JSON.parse(fieldsJsonStr);
        const mappedFields = fields.map(f => ({
            field_name: f.field_name || f.name,
            data_type: f.data_type || f.type,
            nullable: f.nullable !== undefined ? f.nullable : true,
            description: f.description || ""
        }));
        
        const res = await fetch(`${API_BASE}/schemas/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                dataset_id: state.selectedSchemaDatasetId,
                schema_version: version,
                field_definitions: mappedFields,
                schema_notes: notes,
                created_by: author
            })
        });
        
        if (res.ok) {
            showToast("Schema draft successfully created!", "success");
            closeSchemaModal();
            // Reset fields
            document.getElementById("schema-version-input").value = "";
            document.getElementById("schema-notes-input").value = "";
            await loadSchemaVersions(state.selectedSchemaDatasetId);
        } else {
            const err = await res.json();
            showToast(`Creation failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("JSON parsing error: Verify format of field definitions array.", "error");
    }
}

// ==========================================================================
// 6. LINEAGE EXPLORER HUB
// ==========================================================================
function renderLineageSelector(filterQuery = "") {
    const list = document.getElementById("lineage-datasets-list");
    list.innerHTML = "";
    
    const filtered = state.datasets.filter(ds => 
        ds.dataset_name.toLowerCase().includes(filterQuery.toLowerCase()) ||
        ds.canonical_id.toLowerCase().includes(filterQuery.toLowerCase())
    );
    
    filtered.forEach(ds => {
        const item = document.createElement("div");
        item.className = `lineage-selector-item ${state.selectedLineageDatasetId === ds.id ? 'active' : ''}`;
        item.innerHTML = `
            <div class="selector-item-name">${ds.dataset_name}</div>
            <div class="selector-item-meta">
                <span>${ds.canonical_id}</span>
            </div>
        `;
        item.addEventListener("click", () => selectLineageDataset(ds));
        list.appendChild(item);
    });
}

async function selectLineageDataset(ds) {
    state.selectedLineageDatasetId = ds.id;
    
    // Highlight
    document.querySelectorAll(".lineage-selector-item").forEach(item => item.classList.remove("active"));
    renderLineageSelector(document.getElementById("lineage-dataset-search").value);
    
    document.getElementById("lineage-canvas-empty").style.display = "none";
    document.getElementById("lineage-canvas-container").style.display = "block";
    document.getElementById("btn-add-relationship").style.display = "inline-flex";
    
    document.getElementById("lineage-canvas-title").textContent = `Lineage: ${ds.dataset_name}`;
    
    await drawLineageGraph(ds);
}

async function drawLineageGraph(rootDs) {
    const nodesContainer = document.getElementById("lineage-graph-nodes");
    const svg = document.getElementById("lineage-graph-svg");
    
    nodesContainer.innerHTML = "";
    svg.innerHTML = `
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--text-muted)" />
            </marker>
        </defs>
    `;
    
    try {
        const res = await fetch(`${API_BASE}/relationships/dataset/${rootDs.id}`);
        if (res.ok) {
            const relationships = await res.json();
            
            // Build tree representation
            // We want horizontally aligned nodes: parents (left), root (middle), children (right)
            const parentNodes = [];
            const childNodes = [];
            
            relationships.forEach(rel => {
                if (rel.child_dataset_id === rootDs.id) {
                    // This is a parent dataset
                    const p = state.datasets.find(d => d.id === rel.parent_dataset_id);
                    if (p) parentNodes.push({ dataset: p, rel });
                } else if (rel.parent_dataset_id === rootDs.id) {
                    // This is a child dataset
                    const c = state.datasets.find(d => d.id === rel.child_dataset_id);
                    if (c) childNodes.push({ dataset: c, rel });
                }
            });
            
            // Position parameters
            const rootX = 400;
            const rootY = 220;
            
            const parentX = 100;
            const childX = 700;
            
            const parentYStart = Math.max(80, rootY - (parentNodes.length * 90) / 2);
            const childYStart = Math.max(80, rootY - (childNodes.length * 90) / 2);
            
            const allNodes = [];
            
            // Draw Root
            const rootNodeEl = createNodeEl(rootDs, rootX, rootY, true);
            nodesContainer.appendChild(rootNodeEl);
            allNodes.push({ id: rootDs.id, x: rootX, y: rootY, el: rootNodeEl });
            
            // Draw Parents
            parentNodes.forEach((pn, idx) => {
                const px = parentX;
                const py = parentYStart + idx * 100;
                const nodeEl = createNodeEl(pn.dataset, px, py);
                nodesContainer.appendChild(nodeEl);
                allNodes.push({ id: pn.dataset.id, x: px, y: py, el: nodeEl });
                
                // Draw connection (Parent -> Root)
                drawBezierConnection(px + 220, py + 30, rootX, rootY + 30, pn.rel.relationship_type);
            });
            
            // Draw Children
            childNodes.forEach((cn, idx) => {
                const cx = childX;
                const cy = childYStart + idx * 100;
                const nodeEl = createNodeEl(cn.dataset, cx, cy);
                nodesContainer.appendChild(nodeEl);
                allNodes.push({ id: cn.dataset.id, x: cx, y: cy, el: nodeEl });
                
                // Draw connection (Root -> Child)
                drawBezierConnection(rootX + 220, rootY + 30, cx, cy + 30, cn.rel.relationship_type);
            });
            
        }
    } catch (err) {
        console.error(err);
        showToast("Error mapping lineage relationships.", "error");
    }
}

function createNodeEl(ds, x, y, isRoot = false) {
    const div = document.createElement("div");
    div.className = `graph-node ${isRoot ? 'active-root' : ''}`;
    div.style.left = `${x}px`;
    div.style.top = `${y}px`;
    
    div.innerHTML = `
        <div class="node-title" title="${ds.dataset_name}">${ds.dataset_name}</div>
        <div class="node-meta">
            <span class="badge ${ds.trust_level.toLowerCase()}" style="font-size:7px; padding:1px 4px;">${ds.trust_level}</span>
            <span class="node-type-label">${ds.domain_primary}</span>
        </div>
    `;
    
    div.addEventListener("click", () => openDatasetDetails(ds.id));
    return div;
}

function drawBezierConnection(x1, y1, x2, y2, type) {
    const svg = document.getElementById("lineage-graph-svg");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    
    // Smooth Bezier Curve coordinates
    const midX = (x1 + x2) / 2;
    const d = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
    
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "var(--border-glass-hover)");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("marker-end", "url(#arrow)");
    path.style.transition = "stroke 0.3s";
    
    // Add text label on hover
    svg.appendChild(path);
}

// Add relationships
function openRelationshipModal() {
    const modal = document.getElementById("relationship-modal-overlay");
    modal.classList.add("active");
    
    const rootDs = state.datasets.find(d => d.id === state.selectedLineageDatasetId);
    
    document.getElementById("relation-parent-name").value = rootDs.dataset_name;
    document.getElementById("relation-parent-id").value = rootDs.id;
    
    // Populate targets (excluding root)
    const select = document.getElementById("relation-child-id");
    select.innerHTML = `<option value="">-- Choose child dataset --</option>`;
    
    state.datasets.forEach(ds => {
        if (ds.id !== rootDs.id) {
            const opt = document.createElement("option");
            opt.value = ds.id;
            opt.textContent = `${ds.dataset_name} (${ds.canonical_id})`;
            select.appendChild(opt);
        }
    });
}

function closeRelationshipModal() {
    document.getElementById("relationship-modal-overlay").classList.remove("active");
}

async function handleCreateRelationship(e) {
    e.preventDefault();
    const parentId = document.getElementById("relation-parent-id").value;
    const childId = document.getElementById("relation-child-id").value;
    const type = document.getElementById("relation-type").value;
    const desc = document.getElementById("relation-desc").value;
    const creator = document.getElementById("relation-creator").value;
    
    try {
        const res = await fetch(`${API_BASE}/relationships/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                parent_dataset_id: parentId,
                child_dataset_id: childId,
                relationship_type: type,
                description: desc,
                created_by: creator
            })
        });
        
        if (res.ok) {
            showToast("Lineage relationship defined successfully!", "success");
            closeRelationshipModal();
            // Reset
            document.getElementById("relation-desc").value = "";
            
            const rootDs = state.datasets.find(d => d.id === state.selectedLineageDatasetId);
            await drawLineageGraph(rootDs);
        } else {
            const err = await res.json();
            showToast(`Failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error creating relationship.", "error");
    }
}

// ==========================================================================
// 7. ONBOARDING PORTAL HUB
// ==========================================================================
async function handleOnboardingSubmit(e) {
    e.preventDefault();
    
    const proposed_canonical_id = document.getElementById("onboard-canonical-id").value;
    const dataset_name = document.getElementById("onboard-name").value;
    const description = document.getElementById("onboard-description").value;
    const domain_primary = document.getElementById("onboard-domain").value;
    const domain_tags = document.getElementById("onboard-tags").value.split(",").map(t => t.trim()).filter(Boolean);
    const source_system = document.getElementById("onboard-source").value;
    const owner_name = document.getElementById("onboard-owner").value;
    const owner_team = document.getElementById("onboard-team").value;
    const submitted_by = document.getElementById("onboard-submitter").value;
    const proposed_trust_level = document.getElementById("onboard-trust").value;
    const proposed_replay_compatibility = document.getElementById("onboard-replay").value;
    const submission_notes = document.getElementById("onboard-notes").value;
    
    try {
        const res = await fetch(`${API_BASE}/onboarding/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                proposed_canonical_id,
                dataset_name,
                description,
                domain_primary,
                domain_tags,
                source_system,
                owner_name,
                owner_team,
                submitted_by,
                proposed_trust_level,
                proposed_replay_compatibility,
                submission_notes
            })
        });
        
        if (res.ok) {
            showToast("Onboarding request submitted successfully for review!", "success");
            
            // Reset form
            document.getElementById("onboarding-submit-form").reset();
            
            await fetchOnboardingQueue();
        } else {
            const err = await res.json();
            showToast(`Submission failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error submitting onboarding request.", "error");
    }
}

function renderOnboardingQueue() {
    const list = document.getElementById("onboarding-queue-list");
    list.innerHTML = "";
    
    if (state.onboardingQueue.length === 0) {
        list.innerHTML = `<p style="color: var(--text-muted); font-size:13px; text-align:center; padding: 48px 0;">No pending onboarding requests awaiting review.</p>`;
        return;
    }
    
    state.onboardingQueue.forEach(req => {
        const item = document.createElement("div");
        item.className = "queue-item card";
        
        item.innerHTML = `
            <div class="queue-item-header">
                <div class="queue-item-title">
                    <h4>${req.dataset_name}</h4>
                    <span>Proposed: ${req.proposed_canonical_id}</span>
                </div>
                <span class="badge provisional">PENDING REVIEW</span>
            </div>
            <p>${req.description || "No description provided."}</p>
            <div class="queue-item-meta">
                <span>By ${req.submitted_by}</span>
                <span>${new Date(req.submitted_at).toLocaleDateString()}</span>
            </div>
            <div class="queue-item-actions">
                <button class="btn btn-primary btn-sm btn-block btn-approve-onboarding" data-id="${req.id}">
                    <i class="fa-solid fa-thumbs-up"></i> Approve
                </button>
                <button class="btn btn-outline btn-sm btn-block btn-reject-onboarding" data-id="${req.id}">
                    <i class="fa-solid fa-thumbs-down"></i> Reject
                </button>
            </div>
        `;
        
        list.appendChild(item);
        
        // Add events
        item.querySelector(".btn-approve-onboarding").addEventListener("click", () => handleReviewOnboarding(req.id, "APPROVED"));
        item.querySelector(".btn-reject-onboarding").addEventListener("click", () => handleReviewOnboarding(req.id, "REJECTED"));
    });
}

async function handleReviewOnboarding(requestId, status) {
    try {
        const note = prompt(`Enter review notes for ${status}:`) || `Reviewed and ${status.toLowerCase()} by UI Operator.`;
        
        const res = await fetch(`${API_BASE}/onboarding/${requestId}/review`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                decision: status,
                reviewed_by: "Lead UI Auditor",
                review_notes: note
            })
        });
        
        if (res.ok) {
            showToast(`Request successfully ${status}!`, "success");
            await fetchOnboardingQueue();
            await fetchDatasets();
            await fetchDashboardSummary();
            renderCatalog();
        } else {
            const err = await res.json();
            showToast(`Review failed: ${err.detail}`, "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error reviewing onboarding request.", "error");
    }
}

// ==========================================================================
// 8. PROVENANCE INTEGRITY AUDIT WIDGET
// ==========================================================================
async function runProvenanceAudit() {
    const ring = document.getElementById("audit-ring-indicator");
    const scoreText = document.getElementById("audit-score-text");
    const title = document.getElementById("audit-status-title");
    const desc = document.getElementById("audit-status-desc");
    const list = document.getElementById("audit-reports-list");
    
    scoreText.textContent = "...";
    title.textContent = "Auditing chains...";
    desc.textContent = "Validating event counts, schema matches, and trust consistency rules...";
    list.innerHTML = "";
    
    try {
        const res = await fetch(`${API_BASE}/discovery/provenance/validate-all`);
        if (res.ok) {
            const reports = await res.json();
            
            // Calculate a score
            const total = reports.length;
            const valid = reports.filter(r => r.valid !== undefined ? r.valid : r.is_valid).length;
            const score = total > 0 ? Math.round((valid / total) * 100) : 100;
            
            scoreText.textContent = `${score}%`;
            
            // Set styles
            ring.className = "audit-ring";
            if (score === 100) {
                ring.classList.add("success");
                title.textContent = "Ecosystem Converged";
                desc.textContent = "All dataset metadata chains are verified, replay-safe, and fully trace-compliant.";
            } else if (score > 60) {
                ring.classList.add("warning");
                title.textContent = "Minor Divergence";
                desc.textContent = `${total - valid} datasets have partial provenance lineage or unverified governance.`;
            } else {
                ring.classList.add("danger");
                title.textContent = "High Risk Divergence";
                desc.textContent = "Significant gaps detected in metadata lineage. Some datasets lack origins!";
            }
            
            // Render individual reports
            reports.forEach(rep => {
                const item = document.createElement("div");
                item.className = "audit-item";
                const isCompliant = rep.valid !== undefined ? rep.valid : rep.is_valid;
                const eventCount = rep.record_count !== undefined ? rep.record_count : rep.event_count;
                item.innerHTML = `
                    <div class="audit-item-info">
                        <h5>${rep.canonical_id}</h5>
                        <p>Event count: ${eventCount} • Last event: ${rep.last_event_type || 'None'}</p>
                    </div>
                    <span class="audit-status-indicator ${isCompliant ? 'pass' : 'fail'}">
                        ${isCompliant ? '<i class="fa-solid fa-check"></i> Compliant' : '<i class="fa-solid fa-xmark"></i> Flagged'}
                    </span>
                `;
                list.appendChild(item);
            });
            
            showToast("Global provenance integrity audit completed!", "success");
            
        }
    } catch (err) {
        console.error(err);
        showToast("Error running global audit.", "error");
        scoreText.textContent = "ERR";
        title.textContent = "Audit Failed";
        desc.textContent = "FastAPI server error during lineage validations.";
    }
}

// ==========================================================================
// 9. TOAST NOTIFICATIONS
// ==========================================================================
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "fa-info-circle";
    if (type === "success") icon = "fa-circle-check";
    if (type === "error") icon = "fa-triangle-exclamation";
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Autoremove
    setTimeout(() => {
        toast.style.animation = "slideInRight 0.3s reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
