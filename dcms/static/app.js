const number = new Intl.NumberFormat("en-UG", { maximumFractionDigits: 2 });
const currency = (minor) => `UGX ${number.format(minor / 100)}`;
const minorUnits = (value) => {
  const match = value.trim().match(/^([0-9]{1,9})(?:\.([0-9]{1,2}))?$/);
  return match ? Number(match[1]) * 100 + Number((match[2] || "").padEnd(2, "0")) : null;
};

document.querySelectorAll("[data-print]").forEach((button) => {
  button.addEventListener("click", () => window.print());
});

const sale = document.querySelector("#sale-form");
if (sale) {
  const lines = sale.querySelector("#sale-lines");
  const rate = Number(sale.dataset.vat);
  const addLine = sale.querySelector("#add-line");
  const referenceLabel = sale.querySelector("#reference-label");
  let total = 0;

  function updateSale() {
    let subtotal = 0;
    const rows = lines.querySelectorAll(".sale-line");
    for (const row of rows) {
      const price = Number(row.querySelector("select").selectedOptions[0]?.dataset.price || 0);
      const quantity = Number(row.querySelector("input").value);
      if (Number.isInteger(quantity) && quantity > 0 && quantity <= 10000) {
        subtotal += price * quantity;
      }
      const validQuantity = Number.isInteger(quantity) && quantity > 0 && quantity <= 10000;
      row.querySelector(".line-rate").textContent = number.format(price / 100);
      row.querySelector(".line-amount").textContent = number.format((validQuantity ? price * quantity : 0) / 100);
      row.querySelector(".remove-line").disabled = rows.length === 1;
    }
    addLine.disabled = rows.length >= 50;
    const vat = Math.floor((subtotal * rate + 5000) / 10000);
    total = subtotal + vat;
    sale.querySelector("#subtotal-preview").textContent = currency(subtotal);
    sale.querySelector("#vat-preview").textContent = currency(vat);
    sale.querySelector("#sale-total").textContent = currency(total);
    const channel = sale.querySelector("#payment-channel").value;
    referenceLabel.textContent = {
      mobile_money: "Mobile Money transaction reference (optional)",
      bank_deposit: "Bank deposit slip number (optional)",
    }[channel] || "Payment reference (optional)";
  }

  addLine.addEventListener("click", () => {
    lines.append(sale.querySelector("#new-line").content.cloneNode(true));
    lines.lastElementChild.querySelector("select").focus();
    updateSale();
  });
  lines.addEventListener("click", (event) => {
    if (event.target.matches(".remove-line") && lines.children.length > 1) {
      event.target.closest(".sale-line").remove();
      updateSale();
    }
  });
  sale.addEventListener("input", updateSale);
  sale.querySelector("#use-total").addEventListener("click", () => {
    sale.querySelector("#amount-received").value = (total / 100).toFixed(2);
  });
  updateSale();
}

const close = document.querySelector("#close-form");
if (close) {
  const cash = close.querySelector("#actual-cash");
  const variance = close.querySelector("#variance-preview");
  const explanation = close.querySelector("#explanation");
  const expected = Number(close.dataset.expected);

  function updateVariance() {
    const actual = minorUnits(cash.value);
    const difference = actual === null ? null : actual - expected;
    variance.classList.toggle("deficit", difference !== null && difference < 0);
    variance.classList.toggle("balanced", difference !== null && difference >= 0);
    explanation.required = difference !== null && difference !== 0;
    if (difference === null) {
      variance.textContent = "Enter the cash count to see the variance.";
    } else if (difference === 0) {
      variance.textContent = "Cash balanced";
    } else {
      variance.textContent = `${currency(Math.abs(difference))} ${difference < 0 ? "deficit" : "surplus"}`;
    }
  }

  cash.addEventListener("input", updateVariance);
  updateVariance();
}

const navigationToggle = document.querySelector("#sidebar-toggle");
if (navigationToggle) {
  const narrow = window.matchMedia("(max-width: 760px)");
  function resetNavigation() {
    document.body.classList.remove("sidebar-collapsed", "sidebar-open");
    navigationToggle.setAttribute("aria-expanded", String(!narrow.matches));
  }
  navigationToggle.addEventListener("click", () => {
    const className = narrow.matches ? "sidebar-open" : "sidebar-collapsed";
    const toggled = document.body.classList.toggle(className);
    navigationToggle.setAttribute("aria-expanded", String(narrow.matches ? toggled : !toggled));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && narrow.matches) {
      document.body.classList.remove("sidebar-open");
      navigationToggle.setAttribute("aria-expanded", "false");
    }
  });
  document.querySelector("#sidebar-close").addEventListener("click", () => {
    document.body.classList.remove("sidebar-open");
    navigationToggle.setAttribute("aria-expanded", "false");
    navigationToggle.focus();
  });
  narrow.addEventListener("change", resetNavigation);
  resetNavigation();
}

document.querySelectorAll("[data-filter]").forEach((input) => {
  const table = document.getElementById(input.dataset.filter);
  input.addEventListener("input", () => {
    const query = input.value.trim().toLocaleLowerCase();
    const rows = [...table.querySelectorAll("[data-record]")];
    rows.forEach((row) => { row.hidden = !row.textContent.toLocaleLowerCase().includes(query); });
    table.closest(".list-panel").querySelector(".filter-empty").hidden = !rows.length || rows.some((row) => !row.hidden);
  });
});

const reportPeriod = document.querySelector("#report-period");
if (reportPeriod) {
  ["#report-start", "#report-end"].forEach((selector) => {
    document.querySelector(selector).addEventListener("input", () => { reportPeriod.value = "custom"; });
  });
}
