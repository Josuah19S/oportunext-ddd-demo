"use strict";

const CONFIG = window.APP_CONFIG || {};

const LABELS = {
  in_person: "Presencial",
  remote: "Virtual",
  undergraduate: "Pregrado",
  postgraduate: "Posgrado"
};

// Each resource knows its path, its panel and how to show its fields.
const RESOURCES = {
  volunteering: {
    path: "/volunteering",
    panelId: "panel-volunteering",
    title: (item) => item.title,
    entity: (item) => item.organization,
    tag: (item) => item.modality,
    fields: [
      ["Organización", (item) => item.organization],
      ["Modalidad", (item) => label(item.modality)],
      ["Ubicación", (item) => item.location],
      ["Descripción", (item) => item.description]
    ]
  },
  scholarships: {
    path: "/scholarships",
    panelId: "panel-scholarships",
    title: (item) => item.name,
    entity: (item) => item.institution,
    tag: (item) => item.level,
    fields: [
      ["Institución", (item) => item.institution],
      ["Nivel", (item) => label(item.level)],
      ["País", (item) => item.country],
      ["Descripción", (item) => item.description]
    ]
  }
};

class ApiError extends Error {
  constructor(status) {
    super(`HTTP ${status}`);
    this.status = status;
  }
}

function label(value) {
  return LABELS[value] || value;
}

function isConfigured() {
  const values = [CONFIG.API_BASE_URL, CONFIG.APP_CODE];
  return values.every((value) => typeof value === "string" && value !== "" && !value.includes("<"));
}

async function apiGet(path) {
  let response;
  try {
    response = await fetch(CONFIG.API_BASE_URL + path, {
      headers: { "X-Apig-AppCode": CONFIG.APP_CODE }
    });
  } catch {
    throw new ApiError(0);
  }
  if (!response.ok) {
    throw new ApiError(response.status);
  }
  return response.json();
}

function errorMessage(error) {
  const status = error instanceof ApiError ? error.status : -1;
  if (status === 401 || status === 403) return "No autorizado. Revisa el AppCode.";
  if (status === 404) return "No se encontró el recurso.";
  if (status === 429) return "Demasiadas solicitudes. Intenta de nuevo en un minuto.";
  if (status === 0) return "No se pudo conectar con el servidor.";
  return `Error inesperado (HTTP ${status}).`;
}

function createText(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = text;
  return node;
}

function renderCards(container, resourceKey, items) {
  const resource = RESOURCES[resourceKey];
  container.replaceChildren();
  for (const item of items) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "card";
    card.append(
      createText("span", "card-title", resource.title(item)),
      createText("span", "card-entity", resource.entity(item)),
      createText("span", "tag", label(resource.tag(item)))
    );
    card.addEventListener("click", () => openDetail(resourceKey, item.id));
    container.append(card);
  }
}

async function loadList(resourceKey) {
  const panel = document.getElementById(RESOURCES[resourceKey].panelId);
  const status = panel.querySelector(".status");
  const message = panel.querySelector(".message");
  const cards = panel.querySelector(".cards");

  status.textContent = "Cargando…";
  message.textContent = "";
  cards.replaceChildren();

  try {
    const items = await apiGet(RESOURCES[resourceKey].path);
    renderCards(cards, resourceKey, items);
    status.textContent = items.length === 0 ? "No hay elementos para mostrar." : "";
  } catch (error) {
    status.textContent = "";
    message.textContent = errorMessage(error);
  }
}

function loadAll() {
  return Promise.allSettled([loadList("volunteering"), loadList("scholarships")]);
}

async function openDetail(resourceKey, id) {
  const resource = RESOURCES[resourceKey];
  const dialog = document.getElementById("detail-dialog");
  const title = dialog.querySelector("#detail-title");
  const status = dialog.querySelector(".status");
  const message = dialog.querySelector(".message");
  const fields = dialog.querySelector(".detail-fields");

  title.textContent = "Detalle";
  status.textContent = "Cargando…";
  message.textContent = "";
  fields.replaceChildren();
  if (!dialog.open) dialog.showModal();

  try {
    const item = await apiGet(`${resource.path}/${encodeURIComponent(id)}`);
    title.textContent = resource.title(item);
    for (const [name, getValue] of resource.fields) {
      fields.append(createText("dt", "", name), createText("dd", "", getValue(item)));
    }
    status.textContent = "";
  } catch (error) {
    status.textContent = "";
    message.textContent = errorMessage(error);
  }
}

function setupTabs() {
  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));

  function selectTab(selected) {
    for (const tab of tabs) {
      const isSelected = tab === selected;
      tab.setAttribute("aria-selected", String(isSelected));
      tab.tabIndex = isSelected ? 0 : -1;
      document.getElementById(tab.getAttribute("aria-controls")).hidden = !isSelected;
    }
    selected.focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
      event.preventDefault();
      const step = event.key === "ArrowRight" ? 1 : -1;
      selectTab(tabs[(index + step + tabs.length) % tabs.length]);
    });
  });
}

function init() {
  setupTabs();

  if (!isConfigured()) {
    const warning = document.getElementById("config-warning");
    warning.textContent = "Configura frontend/config.js con el dominio de APIG y el AppCode.";
    warning.hidden = false;
    document.getElementById("reload-button").disabled = true;
    return;
  }

  document.getElementById("reload-button").addEventListener("click", loadAll);
  loadAll();
}

init();
