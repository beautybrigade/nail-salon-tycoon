// Nail Salon Tycoon: the page in the browser (R7, R8).
//
// This file only draws and animates. Every rule (which steps are right, the
// star, the earnings, what the nails look like) comes from the Python server
// in web.py, which calls salon.py. R10 adds the nip-cuticles animation.
// Round 5: when a step needs a choice (a color off the polish wall, R12, or
// a shape when filing the hands, R13), the server says so and this page
// only shows the question; the server decides when to ask and judges it.

"use strict";

const SVG_NS = "http://www.w3.org/2000/svg";
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// R8: one animation per step. Keys match web.py STEP_ANIMATIONS.
// tools: the parts of the picture that play; ms: how long it lasts;
// changeAt: when (0 to 1) the nails switch to their new look.
const ANIMATIONS = {
  "ask-health":     { tools: ["speech"],                       ms: 2400, changeAt: 0 },
  "wash-hands":     { tools: ["soap"],                         ms: 2300, changeAt: 0, washing: true },
  "wash-feet":      { tools: ["foot-bath"],                    ms: 2600, changeAt: 0, washing: true },
  "remove-product": { tools: ["cotton"],                       ms: 1800, changeAt: 0.5 },
  "file-nails":     { tools: ["file"],                         ms: 1800, changeAt: 0.5 },
  "nip-cuticles":   { tools: ["nippers"],                      ms: 1800, changeAt: 0.5 },
  "buff-nails":     { tools: ["buffer"],                       ms: 1800, changeAt: 0.5 },
  "pick-color":     { tools: ["polish-wall", "picked-bottle"], ms: 1200, changeAt: 0 },
  "polish-nails":   { tools: ["bottle", "brush", "sparkles"],  ms: 2400, changeAt: 0.45, sparkleAt: 0.8 },
};

// The client's fingers and toes, drawn pointing toward you.
// x, w: left edge and width; top, tip: where the digit starts and ends.
const HAND_DIGITS = [
  { x: 232, w: 30, top: 170, tip: 270 },                  // pinky
  { x: 266, w: 33, top: 176, tip: 302 },                  // ring
  { x: 303, w: 34, top: 176, tip: 312 },                  // middle
  { x: 341, w: 33, top: 174, tip: 298 },                  // index
  { x: 350, w: 36, top: 112, tip: 222, rotate: -30 },     // thumb
];
const FOOT_DIGITS = [
  { x: 220, w: 27, top: 226, tip: 282, toe: true },
  { x: 251, w: 29, top: 230, tip: 292, toe: true },
  { x: 284, w: 31, top: 232, tip: 298, toe: true },
  { x: 319, w: 32, top: 232, tip: 302, toe: true },
  { x: 354, w: 40, top: 224, tip: 306, toe: true },       // big toe
];

// R13: how to draw each nail shape. The nail runs from its base (top) to the
// fingertip (tip); the free edge past the tip gets the shape.
const SHAPE_PATHS = {
  square: (x, top, w, tip) =>
    `M${x} ${top + 3} Q${x + w / 2} ${top - 3} ${x + w} ${top + 3} L${x + w} ${tip + 6} ` +
    `Q${x + w} ${tip + 8} ${x + w - 2} ${tip + 8} L${x + 2} ${tip + 8} Q${x} ${tip + 8} ${x} ${tip + 6} Z`,
  round: (x, top, w, tip) =>
    `M${x} ${top + 3} Q${x + w / 2} ${top - 3} ${x + w} ${top + 3} L${x + w} ${tip} ` +
    `A${w / 2} 9 0 0 1 ${x} ${tip} Z`,
  almond: (x, top, w, tip) =>
    `M${x} ${top + 3} Q${x + w / 2} ${top - 3} ${x + w} ${top + 3} L${x + w} ${tip - 2} ` +
    `Q${x + w} ${tip + 10} ${x + w / 2} ${tip + 14} Q${x} ${tip + 10} ${x} ${tip - 2} Z`,
  stiletto: (x, top, w, tip) =>
    `M${x} ${top + 3} Q${x + w / 2} ${top - 3} ${x + w} ${top + 3} L${x + w} ${tip - 4} ` +
    `Q${x + w * 0.85} ${tip + 10} ${x + w / 2} ${tip + 22} Q${x + w * 0.15} ${tip + 10} ${x} ${tip - 4} Z`,
};

const state = {
  gameId: null,
  steps: [],
  client: null,
  area: "hands",
  stars: 0,
  busy: false,
};

const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((done) => setTimeout(done, REDUCED ? Math.min(ms, 300) : ms));

// --- Talking to the server ---------------------------------------------------

async function getJson(path) {
  const resp = await fetch(path);
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

async function api(path, body = {}) {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

// --- Drawing the hand and foot ----------------------------------------------

function svgEl(tag, attrs) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function drawDigits(viewId, digits) {
  const group = document.querySelector(`#${viewId} .digits`);
  for (const d of digits) {
    const g = svgEl("g", {});
    if (d.rotate) g.setAttribute("transform", `rotate(${d.rotate} ${d.x + d.w / 2} ${d.top})`);
    g.append(svgEl("rect", {
      class: "digit", x: d.x, y: d.top, width: d.w, height: d.tip - d.top, rx: d.w / 2,
    }));
    // The nail: a long, square tip before filing and a short, round one after.
    const nx = d.x + 5;
    const nw = d.w - 10;
    const nailTop = d.tip - (d.toe ? 30 : 36);
    const nail = svgEl("g", { class: "nail" });
    nail.append(
      svgEl("rect", { class: "nail-base long", x: nx, y: nailTop, width: nw,
                      height: (d.toe ? 30 : 36) + (d.toe ? 6 : 12), rx: 4 }),
      svgEl("rect", { class: "nail-base short", x: nx, y: nailTop, width: nw,
                      height: d.toe ? 28 : 34, rx: nw / 2 }),
      // R13: one outline per filing shape; the look's shape picks which shows.
      ...(d.toe ? [] : Object.entries(SHAPE_PATHS).map(([shape, path]) =>
        svgEl("path", { class: `nail-base shaped shape-${shape}`, d: path(nx, nailTop, nw, d.tip) }))),
      svgEl("circle", { class: "chips", cx: nx + nw * 0.3, cy: nailTop + 22, r: 3.5 }),
      svgEl("circle", { class: "chips", cx: nx + nw * 0.7, cy: nailTop + 10, r: 2.5 }),
      svgEl("ellipse", { class: "shine", cx: nx + nw * 0.32, cy: nailTop + 14,
                         rx: nw * 0.14, ry: 9 }),
      svgEl("ellipse", { class: "gloss", cx: nx + nw * 0.3, cy: nailTop + 12,
                         rx: nw * 0.12, ry: 7 }),
      // R10: the cuticle at the nail's base, ragged until nipped, then neat.
      svgEl("path", { class: "cuticle ragged", d: raggedEdge(nx, nw, nailTop) }),
      svgEl("path", { class: "cuticle neat",
                      d: `M${nx} ${nailTop + 1} Q${nx + nw / 2} ${nailTop - 5} ${nx + nw} ${nailTop + 1}` }),
    );
    g.append(nail);
    group.append(g);
  }
}

// A jagged line across the base of a nail: overgrown cuticle skin.
function raggedEdge(nx, nw, y) {
  const points = 6;
  let d = `M${nx} ${y + 1}`;
  for (let i = 1; i <= points; i++) {
    const x = nx + (nw * i) / points;
    d += ` L${x - nw / points / 2} ${y - 5 + (i % 2) * 2} L${x} ${y + 1}`;
  }
  return d;
}

// Apply the server's nail look for each area (R8: the nails change as you go).
function showNails(nails) {
  const views = { hands: $("hand-view"), feet: $("foot-view") };
  for (const [area, view] of Object.entries(views)) {
    const look = nails[area];
    if (!look) continue;
    view.classList.toggle("has-product", look.has_product);
    view.classList.toggle("filed", look.filed);
    view.classList.toggle("nipped", look.cuticles_nipped);
    view.classList.toggle("buffed", look.buffed);
    view.classList.toggle("polished", look.polish_color !== null);
    clearShape(view);
    if (look.shape) view.classList.add("shaped", `shape-${look.shape}`); // R13
    if (look.polish_hex) view.style.setProperty("--polish", look.polish_hex);
  }
}

function clearShape(view) {
  for (const c of [...view.classList]) {
    if (c === "shaped" || c.startsWith("shape-")) view.classList.remove(c);
  }
}

// R12: put the server's colors on the polish wall's shelves (4 per shelf).
function fillWall(options) {
  const shelf = document.querySelector("#polish-wall .wall-bottles");
  shelf.innerHTML = "";
  options.forEach((o, i) => {
    const x = 44 + (i % 4) * 44;
    const y = i < 4 ? 58 : 128;
    shelf.append(
      svgEl("rect", { x: x + 6, y: y - 12, width: 12, height: 14, rx: 3, fill: "#222034" }),
      svgEl("rect", { x, y, width: 24, height: 38, rx: 7, fill: o.hex, stroke: "#fff", "stroke-width": 2 }),
    );
  });
}

function showArea(area) {
  const changed = state.area !== area;
  state.area = area;
  $("stage").dataset.area = area;
  if (changed && area === "feet") banner("Hands done! Now the feet.");
}

function banner(text) {
  const el = $("banner");
  el.textContent = text;
  el.classList.remove("show");
  void el.offsetWidth; // restart the animation
  el.classList.add("show");
}

// --- Playing a step's animation ----------------------------------------------

function restart(el) {
  el.classList.remove("play");
  void el.getBoundingClientRect(); // forces the browser to notice, so it replays
  el.classList.add("play");
}

async function playStep(reply) {
  const anim = ANIMATIONS[reply.animation];
  if (reply.health_answer) $("speech").textContent = `“${reply.health_answer}”`;
  // R12: the bottle and brush hold the color the player picked (from the server).
  document.documentElement.style.setProperty("--polish", reply.brush_hex);

  const tools = anim.tools.filter((t) => t !== "sparkles").map($);
  tools.forEach(restart);
  const view = $(state.area === "feet" ? "foot-view" : "hand-view");
  if (anim.washing) restart(view), view.classList.add("washing");

  await sleep(anim.ms * anim.changeAt);
  showNails(reply.nails);
  if (anim.sparkleAt) {
    await sleep(anim.ms * (anim.sparkleAt - anim.changeAt));
    restart($("sparkles"));
    await sleep(anim.ms * (1 - anim.sparkleAt));
  } else {
    await sleep(anim.ms * (1 - anim.changeAt));
  }
  view.classList.remove("washing");
  showArea(reply.working_area);
}

// --- The panel ---------------------------------------------------------------

function renderClient(client, number, total) {
  state.client = client;
  state.steps = [];
  $("stat-client").textContent = `Client ${number} of ${total}`;
  const nailsNote = client.has_product
    ? "Has old polish on"
    : "Has bare nails";
  const order = client.areas.length > 1 ? "<li>Do the hands first, then the feet</li>" : "";
  const shape = client.nail_shape ? '<li>Wants <strong class="shape"></strong> nails</li>' : "";
  $("client-card").innerHTML = `
    <span class="time"></span><span class="kind"></span>
    <p class="service"><span class="name"></span> <span class="price"></span></p>
    <ul>
      <li>${nailsNote}</li>
      <li>Wants <span class="swatch"></span><strong class="color"></strong></li>
      ${shape}
      ${order}
    </ul>`;
  const card = $("client-card");
  card.querySelector(".time").textContent = client.time;
  const kind = card.querySelector(".kind");
  kind.textContent = client.kind === "walk-in" ? "Walk-in" : "Appointment";
  kind.classList.add(client.kind);
  card.querySelector(".name").textContent = client.service;
  card.querySelector(".price").textContent = `$${client.price}`;
  card.querySelector(".swatch").style.background = client.polish_hex;
  card.querySelector(".color").textContent = client.polish_color;
  if (client.nail_shape) card.querySelector(".shape").textContent = client.nail_shape;

  // Fresh nails for the new client.
  for (const v of ["hand-view", "foot-view"]) {
    $(v).classList.remove("has-product", "filed", "nipped", "buffed", "polished");
    clearShape($(v)); // R13
  }
  document.documentElement.style.setProperty("--polish", client.polish_hex);
  showNails(client.nails);
  state.area = client.working_area;
  $("stage").dataset.area = client.working_area;
  renderTaken();
}

function renderSteps(steps) {
  const box = $("steps");
  box.innerHTML = "";
  for (const step of steps) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = step.label;
    b.addEventListener("click", () => takeStep(step.id));
    box.append(b);
  }
}

function renderTaken() {
  const list = $("taken");
  list.innerHTML = "";
  if (state.steps.length === 0) {
    list.innerHTML = '<li class="empty">None yet</li>';
    return;
  }
  for (const label of state.steps) {
    const li = document.createElement("li");
    li.textContent = label;
    list.append(li);
  }
}

function setBusy(busy) {
  state.busy = busy;
  document.querySelectorAll(".steps button, #finish").forEach((b) => { b.disabled = busy; });
}

function updateEarned(total) {
  $("stat-earned").textContent = `Earned $${total}`;
  $("stat-stars").textContent = "★".repeat(state.stars);
}

// --- Player actions ------------------------------------------------------------

async function takeStep(stepId) {
  if (state.busy) return;
  setBusy(true);
  try {
    let reply = await api("/api/step", { game_id: state.gameId, step: stepId });
    if (reply.choose) { // round 5: the server wants a color or a shape first
      const choice = await askChoice(reply.choose);
      if (choice === null) return; // cancelled: no step taken
      if (reply.choose.kind === "color") fillWall(reply.choose.options);
      reply = await api("/api/step", { game_id: state.gameId, step: stepId, choice });
    }
    state.steps = reply.steps_taken;
    renderTaken();
    await playStep(reply);
  } catch (err) {
    showError(err);
  } finally {
    setBusy(false);
  }
}

async function finishService() {
  if (state.busy) return;
  setBusy(true);
  try {
    const done = await api("/api/finish", { game_id: state.gameId });
    state.stars += done.result.stars;
    updateEarned(done.total_so_far);
    showResult(done);
  } catch (err) {
    showError(err);
    setBusy(false);
  }
}

// Round 5: show the server's question (polish wall or filing shapes) and
// resolve with the chosen option's id, or null if the player cancels.
function askChoice(choose) {
  return new Promise((resolve) => {
    const modal = openModal(`
      <h2></h2>
      <div class="choices ${choose.kind}"></div>
      <button type="button" class="cancel">Cancel</button>`);
    modal.querySelector("h2").textContent = choose.question;
    const box = modal.querySelector(".choices");
    for (const o of choose.options) {
      const b = document.createElement("button");
      b.type = "button";
      if (choose.kind === "color") {
        const bottle = document.createElement("span");
        bottle.className = "mini-bottle";
        bottle.style.background = o.hex;
        b.append(bottle);
      } else {
        b.append(shapeIcon(o.id));
      }
      const label = document.createElement("span");
      label.textContent = o.label;
      b.append(label);
      b.addEventListener("click", () => { closeModal(); resolve(o.id); });
      box.append(b);
    }
    modal.querySelector(".cancel").addEventListener("click", () => { closeModal(); resolve(null); });
    box.querySelector("button").focus();
  });
}

function shapeIcon(shape) {
  const svg = svgEl("svg", { viewBox: "0 0 40 64", class: "shape-icon", "aria-hidden": "true" });
  svg.append(svgEl("rect", { x: 6, y: 6, width: 28, height: 50, rx: 14, class: "icon-finger" }));
  if (SHAPE_PATHS[shape]) {
    svg.append(svgEl("path", { d: SHAPE_PATHS[shape](11, 10, 18, 40), class: "icon-nail" }));
  }
  return svg;
}

function openModal(html) {
  $("modal").innerHTML = html;
  $("overlay").hidden = false;
  const button = $("modal").querySelector("button");
  if (button) button.focus();
  return $("modal");
}

function closeModal() {
  $("overlay").hidden = true;
}

function showResult(done) {
  const r = done.result;
  let modal;
  if (r.satisfied) {
    confetti();
    modal = openModal(`
      <div class="big-star">★</div>
      <h2>The client is satisfied!</h2>
      <p>They give you a star and pay <strong>$${r.earned}</strong>.</p>
      <button type="button">Next</button>`);
  } else {
    modal = openModal(`
      <div class="no-star">☹</div>
      <h2>The client is not satisfied</h2>
      <p>No star, no payment.</p>
      <p>The correct steps were:</p>
      <ol></ol>
      <button type="button">Next</button>`);
    const ol = modal.querySelector("ol");
    for (const label of done.correct_steps) {
      const li = document.createElement("li");
      li.textContent = label;
      ol.append(li);
    }
  }
  modal.querySelector("button").addEventListener("click", () => {
    closeModal();
    if (done.next_client) {
      renderClient(done.next_client, done.client_number, state.total);
      setBusy(false);
    } else {
      showDay(done.day);
    }
  });
}

function showDay(day) {
  const modal = openModal(`
    <h2>End of the day</h2>
    <table>
      <thead><tr><th>Time</th><th>Client</th><th>Service</th><th>Star</th><th>Earned</th></tr></thead>
      <tbody></tbody>
    </table>
    <p class="total">Total earnings: $${day.total}</p>
    <p class="goal"></p>
    <button type="button">Play another day</button>`);
  const body = modal.querySelector("tbody");
  for (const r of day.results) {
    const tr = document.createElement("tr");
    for (const text of [r.time, r.kind, r.service, r.stars ? "★" : "–", `$${r.earned}`]) {
      const td = document.createElement("td");
      td.textContent = text;
      tr.append(td);
    }
    body.append(tr);
  }
  modal.querySelector(".goal").textContent = day.goal_met
    ? `Daily goal of $${day.goal} met. Great work!`
    : `Daily goal of $${day.goal} not met. Try again tomorrow.`;
  if (day.goal_met) confetti();
  modal.querySelector("button").addEventListener("click", () => {
    closeModal();
    newGame();
  });
}

function showError(err) {
  openModal(`<h2>Oops</h2><p class="msg"></p><button type="button">Start a new day</button>`);
  $("modal").querySelector(".msg").textContent =
    `${err.message}. Is python3 web.py still running?`;
  $("modal").querySelector("button").addEventListener("click", () => {
    closeModal();
    newGame();
  });
}

function confetti() {
  if (REDUCED) return;
  const colors = ["#ff3fa4", "#ffd60a", "#1cc7c1", "#8e44ec", "#ff8c1a", "#2f6bff", "#7bd629"];
  const box = $("confetti");
  for (let i = 0; i < 80; i++) {
    const piece = document.createElement("i");
    piece.style.left = `${Math.random() * 100}vw`;
    piece.style.background = colors[i % colors.length];
    piece.style.animationDelay = `${Math.random() * 0.6}s`;
    piece.style.transform = `rotate(${Math.random() * 360}deg)`;
    box.append(piece);
  }
  setTimeout(() => { box.innerHTML = ""; }, 3200);
}

async function newGame() {
  setBusy(true);
  try {
    const data = await api("/api/new-game");
    state.gameId = data.game_id;
    state.total = data.total_clients;
    state.stars = 0;
    $("stat-goal").textContent = `Goal $${data.goal}`;
    updateEarned(0);
    renderSteps(data.steps);
    renderClient(data.client, data.client_number, data.total_clients);
    setBusy(false);
  } catch (err) {
    showError(err);
  }
}

// --- R9: the rules screen, before the day begins -------------------------------

async function showRules() {
  try {
    const data = await getJson("/api/rules");
    const body = $("rules-body");
    body.innerHTML = "";
    for (const section of data.sections) {
      const h = document.createElement("h3");
      h.textContent = section.heading;
      const ul = document.createElement("ul");
      for (const line of section.lines) {
        const li = document.createElement("li");
        li.textContent = line.trim();
        if (/^\s*\w\.\s/.test(line)) li.className = "numbered"; // "1." or "a." already numbers it
        if (line.startsWith(" ")) li.classList.add("indent");
        ul.append(li);
      }
      body.append(h, ul);
    }
    $("begin").disabled = false;
    $("begin").focus();
  } catch (err) {
    $("rules").hidden = true;
    showError(err);
  }
}

function beginDay() {
  $("rules").hidden = true;
  newGame();
}

// --- Start ---------------------------------------------------------------------

drawDigits("hand-view", HAND_DIGITS);
drawDigits("foot-view", FOOT_DIGITS);
$("finish").addEventListener("click", finishService);
$("begin").addEventListener("click", beginDay);
showRules();
