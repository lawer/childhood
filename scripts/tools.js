const state = {
  ready: false,
  clubA: [],
  clubB: [],
  firstNames: [],
  surnames: [],
  backgrounds: [],
  skills: [],
  lastGangText: "",
};

const paths = {
  clubNames: "../partials/club_names_es.md",
  studentNames: "../partials/student_names_es.md",
  backgrounds: "../partials/backgrounds_es.md",
  skills: "../partials/skills_es.md",
};

document.addEventListener("DOMContentLoaded", async () => {
  bindActions();
  await loadData();
  setText("gang-output", "Listo. Pulsa “Generar pandilla”.");
});

function bindActions() {
  document.querySelector("[data-action='generate-gang']")?.addEventListener("click", generateGang);
  document.querySelector("[data-action='copy-gang']")?.addEventListener("click", copyGang);
  document.querySelector("[data-action='gang-name']")?.addEventListener("click", () => {
    const result = randomGangName();
    setHtml("gang-name-output", renderRollLine(result.name, result.rolls));
  });
  document.querySelector("[data-action='kid-name']")?.addEventListener("click", () => {
    const result = randomKidName();
    setHtml("kid-name-output", renderRollLine(result.name, result.rolls));
  });
  document.querySelector("[data-action='attributes']")?.addEventListener("click", () => {
    const result = randomAttributeSet();
    setHtml("attributes-output", `<strong>1D6: ${result.roll}</strong><br>${result.values.join(", ")}`);
  });
  document.querySelector("[data-action='background']")?.addEventListener("click", () => {
    const result = pickNumbered(state.backgrounds);
    setHtml("background-output", renderNumberedEntry(result));
  });
  document.querySelector("[data-action='skill']")?.addEventListener("click", () => {
    const result = pickNumbered(state.skills);
    setHtml("skill-output", renderNumberedEntry(result));
  });
  document.querySelector("[data-action='roll-dice']")?.addEventListener("click", () => {
    const notation = document.querySelector("#dice-select")?.value ?? "1d6";
    const result = rollNotation(notation);
    setHtml("dice-output", `<strong>${notation.toUpperCase()}: ${result.total}</strong><br>${result.rolls.join(" + ")}`);
  });
}

async function loadData() {
  try {
    const [clubNames, studentNames, backgrounds, skills] = await Promise.all([
      fetchText(paths.clubNames),
      fetchText(paths.studentNames),
      fetchText(paths.backgrounds),
      fetchText(paths.skills),
    ]);

    state.clubA = extractTableValues(clubNames, "### Tabla A: primer bloque");
    state.clubB = extractTableValues(clubNames, "### Tabla B: segundo bloque");
    state.firstNames = extractTableValues(studentNames, "### Nombre o apodo");
    state.surnames = extractTableValues(studentNames, "### Apellido");
    state.backgrounds = extractNumberedSections(backgrounds);
    state.skills = extractNumberedSections(skills);
    state.ready = true;
  } catch (error) {
    console.error(error);
    setText("gang-output", "No se han podido cargar las tablas. Revisa que la página se sirva desde un servidor o GitHub Pages.");
  }
}

async function fetchText(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`No se pudo cargar ${path}: ${response.status}`);
  }
  return response.text();
}

function extractTableValues(markdown, heading) {
  const start = markdown.indexOf(heading);
  if (start < 0) {
    return [];
  }
  const rest = markdown.slice(start + heading.length);
  const nextHeading = rest.search(/\n###\s+/);
  const section = nextHeading >= 0 ? rest.slice(0, nextHeading) : rest;
  const values = [];

  for (const line of section.split("\n")) {
    if (!line.trim().startsWith("|")) {
      continue;
    }
    if (/^\|\s*-/.test(line) || /\bD100\b/i.test(line)) {
      continue;
    }
    const cells = line.split("|").slice(1, -1).map((cell) => cell.trim());
    for (let index = 0; index < cells.length; index += 2) {
      const roll = Number.parseInt(cells[index], 10);
      const value = cells[index + 1];
      if (Number.isFinite(roll) && value) {
        values[roll] = value;
      }
    }
  }

  return compactD100(values);
}

function compactD100(values) {
  const out = [];
  for (let roll = 1; roll <= 100; roll += 1) {
    if (values[roll]) {
      out.push({ roll, value: values[roll] });
    }
  }
  return out;
}

function extractNumberedSections(markdown) {
  const headingRegex = /^###\s+(\d{1,3})\.\s+(.+?)\s*$/gm;
  const entries = [];
  const headings = [...markdown.matchAll(headingRegex)];
  for (let index = 0; index < headings.length; index += 1) {
    const match = headings[index];
    const next = headings[index + 1];
    const roll = Number.parseInt(match[1], 10);
    const title = cleanup(match[2]);
    const start = match.index + match[0].length;
    const end = next ? next.index : markdown.length;
    const body = cleanup(markdown.slice(start, end)).replace(/\n+/g, " ");
    if (Number.isFinite(roll) && title) {
      entries.push({ roll, title, body });
    }
  }
  return entries;
}

function randomGangName() {
  ensureReady();
  const first = pickD100(state.clubA);
  const second = pickD100(state.clubB);
  return {
    name: `${first.value} ${second.value}`,
    rolls: `Tabla A ${first.roll}, Tabla B ${second.roll}`,
  };
}

function randomKidName() {
  ensureReady();
  const first = pickD100(state.firstNames);
  const second = pickD100(state.surnames);
  return {
    name: `${first.value} ${second.value}`,
    rolls: `Nombre ${first.roll}, Apellido ${second.roll}`,
  };
}

function randomAttributeSet() {
  const roll = die(6);
  if (roll <= 2) {
    return { roll, values: ["+2", "0", "0", "−2"] };
  }
  if (roll <= 4) {
    return { roll, values: ["0", "0", "0", "0"] };
  }
  return { roll, values: ["+1", "0", "0", "−1"] };
}

function generateGang() {
  try {
    ensureReady();
    const gangName = randomGangName();
    const usedBackgrounds = new Set();
    const kids = [];

    for (let index = 0; index < 4; index += 1) {
      const kidName = randomKidName();
      const attributes = assignAttributes(randomAttributeSet().values);
      const background = pickUniqueNumbered(state.backgrounds, usedBackgrounds);
      kids.push({ kidName, attributes, background });
    }

    const html = [
      `<h3>${escapeHtml(gangName.name)}</h3>`,
      `<p><strong>Tiradas:</strong> ${escapeHtml(gangName.rolls)} · <strong>Chapas iniciales:</strong> 50 · <strong>Ánimo inicial:</strong> 8</p>`,
      `<div class="kid-list">`,
      ...kids.map(renderKidCard),
      `</div>`,
    ].join("");

    state.lastGangText = textGang(gangName, kids);
    setHtml("gang-output", html);
  } catch (error) {
    console.error(error);
    setText("gang-output", "No se pudo generar la pandilla. Las tablas aún no están listas.");
  }
}

function assignAttributes(values) {
  const shuffled = [...values].sort(() => Math.random() - 0.5);
  const mind = parseSigned(shuffled[0]);
  const heart = parseSigned(shuffled[1]);
  const body = parseSigned(shuffled[2]);
  const cool = parseSigned(shuffled[3]);
  return {
    mind,
    heart,
    body,
    cool,
    health: 5 + heart,
    movement: Math.ceil((5 + body) / 2),
  };
}

function renderKidCard(kid, index) {
  const a = kid.attributes;
  return `
    <article class="kid-card">
      <h4>${index + 1}. ${escapeHtml(kid.kidName.name)}</h4>
      <p><strong>Tiradas:</strong> ${escapeHtml(kid.kidName.rolls)} · <strong>Trasfondo ${kid.background.roll}:</strong> ${escapeHtml(kid.background.title)}</p>
      <dl>
        <div><dt>Mente</dt><dd>${formatSigned(a.mind)}</dd></div>
        <div><dt>Corazón</dt><dd>${formatSigned(a.heart)}</dd></div>
        <div><dt>Cuerpo</dt><dd>${formatSigned(a.body)}</dd></div>
        <div><dt>Molar</dt><dd>${formatSigned(a.cool)}</dd></div>
        <div><dt>Salud</dt><dd>${a.health}</dd></div>
        <div><dt>Movimiento</dt><dd>${a.movement} casillas</dd></div>
      </dl>
      <p>${escapeHtml(kid.background.body)}</p>
    </article>
  `;
}

function textGang(gangName, kids) {
  const lines = [
    gangName.name,
    `Tiradas: ${gangName.rolls}`,
    "Chapas iniciales: 50",
    "Ánimo inicial: 8",
    "",
  ];
  kids.forEach((kid, index) => {
    const a = kid.attributes;
    lines.push(`${index + 1}. ${kid.kidName.name}`);
    lines.push(`   ${kid.kidName.rolls}`);
    lines.push(`   Mente ${formatSigned(a.mind)}, Corazón ${formatSigned(a.heart)}, Cuerpo ${formatSigned(a.body)}, Molar ${formatSigned(a.cool)}`);
    lines.push(`   Salud ${a.health}, Movimiento ${a.movement} casillas`);
    lines.push(`   Trasfondo ${kid.background.roll}: ${kid.background.title}`);
    lines.push("");
  });
  return lines.join("\n");
}

async function copyGang() {
  if (!state.lastGangText) {
    generateGang();
  }
  try {
    await navigator.clipboard.writeText(state.lastGangText);
    setText("gang-output", `${state.lastGangText}\n\nCopiado al portapapeles.`);
  } catch {
    setText("gang-output", `${state.lastGangText}\n\nNo se pudo copiar automáticamente; selecciona el texto y cópialo manualmente.`);
  }
}

function pickD100(entries) {
  if (!entries.length) {
    throw new Error("Tabla D100 vacía");
  }
  const roll = die(100);
  return entries.find((entry) => entry.roll === roll) ?? entries[roll % entries.length];
}

function pickNumbered(entries) {
  ensureReady();
  if (!entries.length) {
    throw new Error("Tabla numerada vacía");
  }
  return entries[Math.floor(Math.random() * entries.length)];
}

function pickUniqueNumbered(entries, used) {
  let entry = pickNumbered(entries);
  let guard = 0;
  while (used.has(entry.roll) && guard < 200) {
    entry = pickNumbered(entries);
    guard += 1;
  }
  used.add(entry.roll);
  return entry;
}

function rollNotation(notation) {
  const match = /^(\d+)d(\d+)$/i.exec(notation.trim());
  if (!match) {
    throw new Error(`Notación no válida: ${notation}`);
  }
  const count = Number.parseInt(match[1], 10);
  const sides = Number.parseInt(match[2], 10);
  const rolls = Array.from({ length: count }, () => die(sides));
  return {
    rolls,
    total: rolls.reduce((sum, value) => sum + value, 0),
  };
}

function die(sides) {
  return Math.floor(Math.random() * sides) + 1;
}

function ensureReady() {
  if (!state.ready) {
    throw new Error("Datos no cargados");
  }
}

function renderRollLine(name, rolls) {
  return `<strong>${escapeHtml(name)}</strong><br><span>${escapeHtml(rolls)}</span>`;
}

function renderNumberedEntry(entry) {
  return `<strong>${entry.roll}. ${escapeHtml(entry.title)}</strong><br>${escapeHtml(entry.body)}`;
}

function parseSigned(value) {
  return Number.parseInt(String(value).replace("−", "-").replace("+", ""), 10) || 0;
}

function formatSigned(value) {
  if (value > 0) {
    return `+${value}`;
  }
  if (value < 0) {
    return `−${Math.abs(value)}`;
  }
  return "0";
}

function cleanup(value) {
  return value
    .replace(/\*\*/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function setHtml(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.innerHTML = value;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
