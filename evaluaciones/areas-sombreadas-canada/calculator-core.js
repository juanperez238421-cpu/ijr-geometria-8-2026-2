"use strict";
/**
 * Evaluador aritmético seguro para la calculadora de Geometría 8.
 * Sin eval/Function, sin red, sin soluciones de la evaluación.
 * Se utiliza π = 3.14 conforme a las instrucciones del examen.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root && typeof root === "object") root.GeometryCalculatorCore = api;
})(typeof globalThis === "object" ? globalThis : undefined, function () {
  const PI = 3.14;
  const MAX_EXPRESSION = 120;
  function tokenize(text) {
    if (typeof text !== "string" || !text.trim() || text.length > MAX_EXPRESSION) {
      throw new Error("La operación está vacía o es demasiado larga.");
    }
    const value = text.replace(/,/g, ".").replace(/[−–]/g, "-").replace(/×/g, "*").replace(/÷/g, "/");
    const tokens = [];
    let pos = 0;
    while (pos < value.length) {
      if (/\s/.test(value[pos])) { pos++; continue; }
      const tail = value.slice(pos);
      const n = tail.match(/^(?:\d+(?:\.\d*)?|\.\d+)/);
      if (n) {
        const num = Number(n[0]);
        if (!Number.isFinite(num)) throw new Error("Número fuera de rango.");
        tokens.push({kind:"number",value:num});
        pos += n[0].length;
        continue;
      }
      const ch = value[pos];
      if (ch === "π") tokens.push({kind:"number",value:PI});
      else if ("+-*/^()%".includes(ch)) tokens.push({kind:ch});
      else throw new Error("Símbolo no admitido.");
      pos++;
    }
    return tokens;
  }
  function evaluate(text) {
    const tokens = tokenize(text);
    let i = 0;
    const peek = () => tokens[i]?.kind;
    const take = (kind) => {
      if (peek() !== kind) throw new Error("Revisa la operación y los paréntesis.");
      i++;
    };
    function primary() {
      if (peek() === "number") return tokens[i++].value;
      if (peek() === "(") {
        take("(");
        const n = addition();
        take(")");
        return n;
      }
      throw new Error("Falta un número o paréntesis.");
    }
    function postfix() {
      let n = primary();
      while (peek() === "%") { take("%"); n /= 100; }
      return n;
    }
    // Right-associative power; -3^2 is interpreted as -(3^2).
    function power() {
      let n = postfix();
      if (peek() === "^") { take("^"); n = Math.pow(n, unary()); }
      return n;
    }
    function unary() {
      if (peek() === "+") { take("+"); return unary(); }
      if (peek() === "-") { take("-"); return -unary(); }
      return power();
    }
    function multiplication() {
      let n = unary();
      while (peek() === "*" || peek() === "/") {
        const op = peek(); i++;
        const right = unary();
        if (op === "/" && right === 0) throw new Error("No se puede dividir entre cero.");
        n = op === "*" ? n * right : n / right;
      }
      return n;
    }
    function addition() {
      let n = multiplication();
      while (peek() === "+" || peek() === "-") {
        const op = peek(); i++;
        const right = multiplication();
        n = op === "+" ? n + right : n - right;
      }
      return n;
    }
    const result = addition();
    if (i !== tokens.length) throw new Error("La operación contiene símbolos incompletos.");
    if (!Number.isFinite(result) || Math.abs(result) > 1e12) {
      throw new Error("Resultado fuera del rango admitido.");
    }
    return Object.is(result, -0) ? 0 : result;
  }
  function format(result) {
    if (!Number.isFinite(result)) throw new Error("Resultado no válido.");
    if (result === 0) return "0";
    const fixed = result.toFixed(9).replace(/0+$/, "").replace(/\.$/, "");
    // Tiny nonzero values should not be silently transferred as zero.
    if (Number(fixed) === 0) throw new Error("Resultado demasiado pequeño para mostrarlo.");
    return fixed;
  }
  return { PI, tokenize, evaluate, format, MAX_EXPRESSION };
});
