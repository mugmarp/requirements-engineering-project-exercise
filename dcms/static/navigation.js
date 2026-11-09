/* Per-tab return paths, unsaved-entry protection and explicit posting reviews. */
(() => {
  const storageKey = "dcms.navigation.v1";
  const pendingKey = "dcms.navigation.return";
  const here = () => document.body.dataset.navigationUrl || location.pathname + location.search;
  const localPath = (value) => {
    try {
      const url = new URL(value, location.origin);
      return url.origin === location.origin && !url.pathname.startsWith("/work/")
        ? url.pathname + url.search : null;
    } catch { return null; }
  };
  const read = (key) => { try { return sessionStorage.getItem(key); } catch { return null; } };
  const store = (key, value) => { try { sessionStorage.setItem(key, value); } catch { /* Server fallback links remain usable. */ } };
  let trail = [];
  try { trail = JSON.parse(read(storageKey) || "[]"); } catch { trail = []; }
  if (!Array.isArray(trail)) trail = [];
  trail = trail.filter((entry) => entry && localPath(entry.url) && typeof entry.title === "string");
  const previousVisit = trail.findLastIndex((entry) => entry.url === here());
  const browserReturn = performance.getEntriesByType("navigation")[0]?.type === "back_forward";
  if ((read(pendingKey) === here() || browserReturn) && previousVisit >= 0) {
    trail = trail.slice(0, previousVisit + 1);
  }
  store(pendingKey, "");
  if (trail.at(-1)?.url !== here()) {
    trail.push({ url: here(), title: document.body.dataset.pageTitle || "previous page" });
  }
  trail = trail.slice(-30);
  store(storageKey, JSON.stringify(trail));
  const previous = trail.length > 1 ? trail.at(-2) : null;
  document.querySelectorAll("[data-back]").forEach((link) => {
    if (!previous) return;
    link.href = localPath(previous.url);
    if (link.hasAttribute("data-return-label")) link.textContent = `← Back to ${previous.title}`;
    link.hidden = false;
  });
  document.addEventListener("dcms:locationchange", () => {
    if (trail.length) trail[trail.length - 1].url = here();
    store(storageKey, JSON.stringify(trail));
  });

  const guards = [...document.querySelectorAll("form[data-dirty-guard]")];
  const fingerprint = (form) => JSON.stringify([...new FormData(form)]
    .filter(([key]) => !["csrf", "request_key", "revision"].includes(key)));
  const initial = new Map(guards.map((form) => [form, fingerprint(form)]));
  const dirty = (form) => form.dataset.unsaved === "true" || fingerprint(form) !== initial.get(form);
  const dirtyForms = () => guards.filter(dirty);
  let submitting = false;
  let reviewing = false;
  const draftNotice = document.querySelector("#draft-notice");
  const workflowNotice = document.querySelector("#workflow-notice");
  function refreshDraftNotice() { draftNotice.hidden = !dirtyForms().length; }
  document.addEventListener("input", refreshDraftNotice);
  document.addEventListener("change", refreshDraftNotice);
  document.addEventListener("click", () => setTimeout(refreshDraftNotice, 0));
  refreshDraftNotice();
  window.addEventListener("beforeunload", (event) => {
    if (!submitting && dirtyForms().length) {
      event.preventDefault();
      event.returnValue = "";
    }
  });

  const dialog = document.querySelector("#action-dialog");
  const cancelButton = document.querySelector("#dialog-cancel");
  const confirmButton = document.querySelector("#dialog-confirm");
  function review(title, message, action, cancel = "Keep editing", requireReason = false) {
    const reason = document.querySelector("#dialog-reason");
    reason.value = "";
    reason.required = requireReason;
    document.querySelector("#dialog-reason-label").hidden = !requireReason;
    reviewing = true;
    document.querySelector("#action-dialog-title").textContent = title;
    document.querySelector("#action-dialog-message").textContent = message;
    confirmButton.textContent = action;
    cancelButton.textContent = cancel;
    return new Promise((resolve) => {
      const settle = (accepted) => {
        dialog.close();
        cancelButton.onclick = null;
        confirmButton.onclick = null;
        dialog.oncancel = null;
        reviewing = false;
        resolve(accepted);
      };
      cancelButton.onclick = () => settle(false);
      confirmButton.onclick = () => { if (!requireReason || (reason.value.trim() && reason.reportValidity())) settle(true); else reason.reportValidity(); };
      dialog.oncancel = (event) => { event.preventDefault(); settle(false); };
      dialog.showModal();
      cancelButton.focus();
    });
  }
  document.addEventListener("click", async (event) => {
    const link = event.target.closest("a[href]");
    if (!link || event.defaultPrevented || event.button !== 0) return;
    const destination = new URL(link.href, location.href);
    if (destination.href === location.href || (destination.pathname === location.pathname && destination.search === location.search && destination.hash)) return;
    const unsaved = dirtyForms().length > 0;
    // Modifier/new-tab actions leave the current form intact.
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || link.target === "_blank") return;
    if (unsaved || link.hasAttribute("data-back")) {
      event.preventDefault();
      if (reviewing) return;
      if (unsaved && !await review("Discard unsaved entries?", "Your unposted entries on this page will be discarded. Saved transactions will remain available.", "Discard and leave")) return;
      if (link.hasAttribute("data-back")) store(pendingKey, localPath(link.href) || "");
      // Suppress the unload warning after an explicit discard decision.
      submitting = true;
      location.assign(link.href);
    }
  });

  function notice(message) {
    workflowNotice.textContent = message;
    workflowNotice.hidden = false;
    workflowNotice.scrollIntoView({ block: "center", behavior: "smooth" });
  }
  const day = document.body.dataset.businessDate;
  document.querySelectorAll('form[method="post"]').forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (submitting || reviewing) return;
      if (!form.reportValidity()) return;
      workflowNotice.hidden = true;
      const fields = new FormData(form);
      const field = (key) => String(fields.get(key) || "").trim();
      const otherDirty = dirtyForms().filter((candidate) => candidate !== form);
      if (form.dataset.review === "close" && otherDirty.length) {
        notice("Save or clear the pending cash expense and opening-cash entries before closing this date. They are not included in expected cash yet.");
        return;
      }
      let title = "Review action";
      let message = "";
      let action = "Save";
      let needsReason = false;
      switch (form.dataset.review) {
        case "sale": {
          let subtotal = 0;
          const descriptions = [];
          for (const row of form.querySelectorAll(".sale-line")) {
            const product = row.querySelector("select").selectedOptions[0];
            const quantity = Number(row.querySelector("input").value);
            subtotal += Number(product?.dataset.price || 0) * quantity;
            descriptions.push(`${quantity} × ${product?.textContent.split(" · ")[0] || "product"}`);
          }
          const total = subtotal + Math.floor((subtotal * Number(form.dataset.vat) + 5000) / 10000);
          if (minorUnits(field("received")) !== total) {
            notice("Amount received must equal the total due. Confirm full payment before posting the sale.");
            return;
          }
          title = "Post this paid sale?";
          action = "Post sale";
          message = `Business date: ${day}\nCustomer: ${field("customer")}\n${descriptions.join("\n")}\nPayment: ${form.querySelector("#payment-channel").selectedOptions[0].textContent}\nTotal paid: ${currency(total)}\n\nPosting deducts stock and creates a saved receipt. Confirm that payment has been received.`;
          break;
        }
        case "close": {
          const actual = minorUnits(field("actual_cash"));
          if (actual === null) { notice("Enter a valid physical cash count before closing."); return; }
          const expected = Number(form.dataset.expected);
          title = "Close and lock this date?";
          action = "Close date";
          message = `Business date: ${day}\nExpected cash: ${currency(expected)}\nCash counted: ${currency(actual)}\nVariance: ${currency(actual - expected)}\nExplanation: ${field("explanation") || "Cash balanced"}\n\nThis saves the final report and locks sales, expenses, opening cash and attendance for this date.`;
          break;
        }
        case "expense":
          title = "Record this cash expense?";
          action = "Record expense";
          message = `Business date: ${day}\n${field("description")}\nAmount: UGX ${field("amount")}\n\nThis cash outflow reduces expected cash. Record wages here only when actually paid.`;
          break;
        case "opening":
          title = "Save opening cash?";
          message = `Business date: ${day}\nOpening cash: UGX ${field("amount")}\n\nThis changes the expected cash calculation.`;
          break;
        case "worker":
          title = "Add this worker?";
          action = "Add worker";
          message = `${field("code")} · ${field("name")}\nDaily rate: UGX ${field("daily_rate")}\nStart date: ${field("started_on") || day}\n\nRegistration does not mark attendance or record a wage payment.`;
          break;
        case "worker-update":
          title = "Save worker changes?";
          message = `Rate: UGX ${field("daily_rate")} from ${field("effective_from")}\nLast working date: ${field("ended_on") || "Ongoing"}\nExisting attendance amounts remain unchanged.`;
          break;
        case "bank-account":
          title = "Register bank account?";
          message = `${field("name")} · ${field("bank_name")} · last four digits ${field("suffix")}\nThis does not connect to the bank.`;
          break;
        case "bank-import":
          title = "Import reviewed statement rows?";
          message = "Import the rows shown in the preview. Identical transaction IDs in the same account are skipped; changed values are rejected. No sales will be created.";
          action = "Import rows";
          break;
        case "bank-reverse":
          title = "Reverse this bank allocation?";
          message = `Reason: ${field("reason")}\nThe credit and receipt become available for matching again. The allocation event is retained; sales and cash reports are unchanged.`;
          action = "Reverse allocation";
          break;
        case "bank-match":
          title = "Save bank allocation?";
          message = `Statement: ${form.querySelector('[name="transaction_id"]').selectedOptions[0].textContent}\nReceipt: ${form.querySelector('[name="sale_id"]').selectedOptions[0].textContent}\nAllocation: UGX ${field("amount")}\nThis links existing records without creating another sale.`;
          action = "Save allocation";
          break;
        case "attendance":
          if (form.dataset.currentStatus) {
            needsReason = true;
            title = "Change recorded attendance?";
            action = "Change attendance";
            message = `${form.dataset.workerName}\nBusiness date: ${day}\n${form.dataset.currentStatus} → ${event.submitter.value}\n\nThis updates wage eligibility, not wages paid.`;
          }
          break;
      }
      if (otherDirty.length) message += "\n\nOther unsaved entries on this page will be discarded when the page refreshes.";
      if (message && !await review(title, message.trim(), action, "Keep editing", needsReason)) return;
      if (needsReason) {
        const reason = document.createElement("input"); reason.type="hidden"; reason.name="reason";
        reason.value=document.querySelector("#dialog-reason").value.trim(); form.append(reason);
      }
      if (!form.reportValidity()) return;
      // Preserve clicked attendance status before disabling duplicate submissions.
      if (event.submitter?.name) {
        const choice = document.createElement("input");
        choice.type = "hidden";
        choice.name = event.submitter.name;
        choice.value = event.submitter.value;
        form.append(choice);
      }
      submitting = true;
      document.querySelectorAll('button[type="submit"]').forEach((button) => { button.disabled = true; });
      HTMLFormElement.prototype.submit.call(form);
    });
  });
})();
