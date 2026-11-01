document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("menuToggle");
  const overlay = document.getElementById("mobileOverlay");

  function closeMenu() {
    if (sidebar) sidebar.classList.remove("sidebar-open");
    if (overlay) overlay.classList.remove("overlay-visible");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
  if (toggle && sidebar && overlay) {
    toggle.addEventListener("click", () => {
      const isOpen = sidebar.classList.toggle("sidebar-open");
      overlay.classList.toggle("overlay-visible", isOpen);
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
    overlay.addEventListener("click", closeMenu);
  }

  document.querySelectorAll(".notice-close").forEach(button => {
    button.addEventListener("click", () => button.closest(".notice")?.remove());
  });

  const toast = document.getElementById("toast");
  function showToast(message) {
    if (!toast) {
      alert(message);
      return;
    }
    toast.textContent = message;
    toast.classList.add("toast-visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove("toast-visible"), 3200);
  }

  const contributionForm = document.getElementById("contributionForm");
  if (contributionForm) {
    const dateField = document.getElementById("contributionDate");
    if (dateField && !dateField.value) {
      const today = new Date();
      dateField.value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
    }
    contributionForm.addEventListener("submit", event => {
      event.preventDefault();
      showToast("Preview only: contribution saving will be implemented in Phase 3.");
    });
  }

  const memberForm = document.getElementById("memberForm");
  if (memberForm) memberForm.addEventListener("submit", event => {
    event.preventDefault();
    showToast("Preview only: member records will be saved in a later phase.");
  });

  const settingsForm = document.getElementById("settingsForm");
  if (settingsForm) settingsForm.addEventListener("submit", event => {
    event.preventDefault();
    showToast("Preview only: settings are not saved permanently yet.");
  });

  ["loginForm", "registerForm"].forEach(id => {
    const form = document.getElementById(id);
    if (form) form.addEventListener("submit", event => {
      event.preventDefault();
      showToast("Authentication will be implemented in Phase 2.");
    });
  });

  const searchPairs = [
    ["tableSearch", "contributionTable"],
    ["historySearch", "historyTable"],
  ];
  searchPairs.forEach(([inputId, tableId]) => {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      table.querySelectorAll("tbody tr").forEach(row => {
        row.hidden = !row.textContent.toLowerCase().includes(query);
      });
    });
  });

  const addMemberBtn = document.getElementById("addMemberBtn");
  if (addMemberBtn) addMemberBtn.addEventListener("click", () => {
    document.getElementById("memberName")?.focus();
    document.getElementById("memberName")?.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  const editRotationBtn = document.getElementById("editRotationBtn");
  if (editRotationBtn) editRotationBtn.addEventListener("click", () => showToast("Rotation management will be connected in Phase 3."));
  const payoutInfoBtn = document.getElementById("payoutInfoBtn");
  if (payoutInfoBtn) payoutInfoBtn.addEventListener("click", () => showToast("Payout details will be connected to saved records in Phase 3."));
  const exportBtn = document.getElementById("exportBtn");
  if (exportBtn) exportBtn.addEventListener("click", () => showToast("Report export will be implemented after database reports are available."));
});
