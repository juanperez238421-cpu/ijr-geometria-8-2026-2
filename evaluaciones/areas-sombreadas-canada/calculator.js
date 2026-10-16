"use strict";
/**
 * Calculadora accesible integrada; no escribe directamente en Supabase.
 * "Usar resultado" dispara el evento input existente para autoguardado.
 */
(() => {
  const core = globalThis.GeometryCalculatorCore;
  const panel = document.getElementById("calculatorPanel");
  if (!panel || !core) return;
  const expressionEl = document.getElementById("calcExpression");
  const resultEl = document.getElementById("calcResult");
  const transferEl = document.getElementById("calcTransfer");
  const hintEl = document.getElementById("calcHint");
  let expression = "";
  let result = null;
  let calculated = false;
  const makeVisible = (text) => {
    expressionEl.textContent = text || "0";
    expressionEl.scrollLeft = expressionEl.scrollWidth;
  };
  function show() {
    makeVisible(expression);
    if (!calculated) {
      resultEl.textContent = expression ? "Pulsa =" : "0";
      transferEl.disabled = true;
    }
  }
  function reset() {
    expression = "";
    result = null;
    calculated = false;
    hintEl.textContent = "Puedes usar el teclado cuando la calculadora tenga el foco.";
    show();
  }
  function append(token) {
    if (calculated) {
      const previous = result === null ? "" : core.format(result);
      expression = ["+","−","×","÷","^","%"].includes(token) ? previous : "";
      calculated = false;
      result = null;
    }
    if (expression.length + token.length > core.MAX_EXPRESSION) {
      hintEl.textContent = "La operación llegó al máximo de caracteres.";
      return;
    }
    if (expression === "" && ["×","÷","^","%"].includes(token)) return;
    expression += token;
    hintEl.textContent = "Pulsa = para calcular el resultado.";
    show();
  }
  function calculate() {
    try {
      const n = core.evaluate(expression);
      const display = core.format(n);
      result = n;
      calculated = true;
      resultEl.textContent = display;
      transferEl.disabled = n < 0;
      hintEl.textContent = n < 0
        ? "El área debe ser no negativa. Revisa el signo antes de transferir."
        : "Resultado listo. Puedes copiarlo a la respuesta.";
    } catch (err) {
      calculated = false;
      result = null;
      transferEl.disabled = true;
      resultEl.textContent = "Error";
      hintEl.textContent = err instanceof Error ? err.message : "Revisa la operación.";
    }
  }
  function handle(action) {
    if (action === "clear") { reset(); return; }
    if (action === "back") {
      if (calculated) { reset(); return; }
      expression = expression.slice(0,-1);
      hintEl.textContent = "Pulsa = para calcular.";
      show();
      return;
    }
    if (action === "equals") { calculate(); return; }
    if (action === "square") { append("^2"); return; }
    if (action === "±") {
      if (calculated && result !== null) expression = core.format(result);
      expression = expression ? "−(" + expression + ")" : "−";
      calculated = false;result = null;
      show();
      return;
    }
    append(action);
  }
  panel.querySelectorAll("[data-calc]").forEach((button) =>
    button.addEventListener("click", () => handle(button.dataset.calc))
  );
  panel.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    // Enter/space on a key should use native button activation.
    if (event.target instanceof HTMLButtonElement && ["Enter"," "].includes(event.key)) return;
    const aliases={"*":"×","/":"÷","-":"−",",":".","p":"π","P":"π","x":"×","X":"×"};
    let action = aliases[event.key] || event.key;
    if (event.key === "Enter" || event.key === "=") action = "equals";
    if (event.key === "Backspace") action = "back";
    if (event.key === "Escape" || event.key === "Delete") action = "clear";
    if (/^[0-9]$/.test(action) || ["+","−","×","÷",".","(",")","%","π","^","equals","back","clear"].includes(action)) {
      event.preventDefault();
      handle(action);
    }
  });
  transferEl.addEventListener("click", () => {
    if (result === null || !calculated || result < 0) return;
    const input = document.getElementById("areaValue");
    if (!input || input.disabled || document.getElementById("examView")?.classList.contains("hidden")) return;
    const text = core.format(result);
    input.value = text;
    input.dispatchEvent(new Event("input", {bubbles:true}));
    input.focus({preventScroll:true});
    hintEl.textContent = "Resultado copiado a tu respuesta. Justifica las operaciones en el espacio correspondiente.";
  });
  reset();
})();
