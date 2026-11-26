const API_BASE_URL = (
  window.VETQUICK_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");
const PAGE_SIZE = 50;
const token = sessionStorage.getItem("vetquick_token");
const veterinarianId = sessionStorage.getItem("vetquick_veterinario_id");

const resourceConfig = {
  tutores: {
    title: "Tutores",
    singular: "tutor",
    description: "Gerencie os responsáveis cadastrados na clínica.",
    endpoint: "/api/tutores/",
    idField: "id_tutores",
    columns: [
      { label: "Tutor", primary: "nome", secondary: "sobrenome" },
      { label: "E-mail", field: "email" },
      { label: "Telefone", field: "telefone" },
      { label: "CPF", field: "cpf_tutor" },
      { label: "Cadastro", field: "datacadastro", format: "date" },
    ],
    fields: [
      { name: "nome", label: "Nome", required: true },
      { name: "sobrenome", label: "Sobrenome", required: true },
      { name: "email", label: "E-mail", type: "email", required: true },
      { name: "telefone", label: "Telefone", required: true },
      { name: "cpf_tutor", label: "CPF", required: true },
      { name: "datacadastro", label: "Data de cadastro", type: "date", required: true, defaultToday: true },
      { name: "cep", label: "CEP", required: false },
      { name: "numero_telefone", label: "Número de telefone (DDD)", required: false },
      { name: "enderecoassociado", label: "ID do endereço", type: "number", required: false },
    ],
  },
  animais: {
    title: "Animais",
    singular: "animal",
    description: "Consulte e mantenha os pacientes da clínica atualizados.",
    endpoint: "/api/animais/",
    idField: "id_animais",
    columns: [
      { label: "Animal", primary: "nome", secondary: "id_animais", secondaryPrefix: "ID " },
      { label: "Tutor", field: "tutor_id", format: "association", lookup: "tutores" },
      { label: "Espécie", field: "especie", format: "association", lookup: "especies" },
      { label: "Raça", field: "raca", format: "association", lookup: "racas" },
      { label: "Peso", field: "peso_atual_kg", suffix: " kg" },
    ],
    fields: [
      { name: "tutor_id", label: "Tutor", type: "select", optionSource: "tutores", required: true },
      { name: "nome", label: "Nome do animal", required: true },
      { name: "idade_estimada", label: "Idade estimada (anos)", type: "number", required: true },
      { name: "sexo", label: "Sexo", required: true },
      { name: "cor", label: "Cor", required: true },
      { name: "peso_atual_kg", label: "Peso atual (kg)", required: true },
      { name: "especie", label: "Espécie", type: "select", optionSource: "especies", required: true },
      { name: "raca", label: "Raça", type: "select", optionSource: "racas", required: true },
      { name: "situacao", label: "Situação", required: true },
      { name: "id_rfid", label: "ID do microchip (RFID)", type: "number", required: true },
      { name: "data_rfid_vinculo", label: "Data de vínculo do microchip", type: "date", required: true, defaultToday: true },
    ],
  },
  consultas: {
    title: "Consultas",
    singular: "consulta",
    description: "Acompanhe e atualize os registros de atendimento.",
    endpoint: "/api/consultas/",
    idField: "id_consulta",
    columns: [
      { label: "Consulta", primary: "motivo", secondary: "id_consulta", secondaryPrefix: "Registro " },
      { label: "Animal (ID)", field: "animal_atendido" },
      { label: "Atendimento", field: "datahora_atendimento", format: "datetime" },
      { label: "Diagnóstico", field: "diagnostico" },
      { label: "Situação", field: "situacao_atual", format: "status" },
    ],
    fields: [
      { name: "animal_atendido", label: "ID do animal", type: "number", required: true },
      { name: "datahora_atendimento", label: "Data e hora do atendimento", type: "datetime-local", required: true, defaultNow: true },
      { name: "motivo", label: "Motivo", type: "textarea", required: true, full: true },
      { name: "anamnese", label: "Anamnese", type: "textarea", required: true, full: true },
      { name: "sintomas", label: "Sintomas", type: "textarea", required: true, full: true },
      { name: "diagnostico", label: "Diagnóstico", type: "textarea", required: true, full: true },
      { name: "tratamento", label: "Tratamento", type: "textarea", required: true, full: true },
      { name: "prescr_medicam", label: "Prescrição de medicamentos", type: "textarea", required: true, full: true },
      { name: "peso_kg", label: "Peso (kg)", required: true },
      { name: "temperatura", label: "Temperatura", required: true },
      { name: "obser", label: "Observações", type: "textarea", required: true, full: true },
      {
        name: "situacao_atual",
        label: "Situação",
        type: "select",
        required: true,
        options: [
          ["agendada", "Agendada"],
          ["realizada", "Realizada"],
          ["cancelada", "Cancelada"],
          ["nao compareceu", "Não compareceu"],
        ],
      },
    ],
  },
  vacinas: {
    title: "Vacinas",
    singular: "vacina",
    description: "Gerencie aplicações, lotes e próximas doses dos pacientes.",
    endpoint: "/api/vacinas/",
    idField: "id_vacina",
    columns: [
      { label: "Vacina", primary: "nome_vacina", secondary: "lote", secondaryPrefix: "Lote " },
      { label: "Animal (ID)", field: "animal_atendido" },
      { label: "Aplicação", field: "data_vacina", format: "date" },
      { label: "Próxima dose", field: "data_prox_dose", format: "date" },
      { label: "Situação", field: "situacao", format: "status" },
    ],
    fields: [
      { name: "animal_atendido", label: "ID do animal", type: "number", required: true },
      { name: "nome_vacina", label: "Nome da vacina", required: true },
      { name: "tipo_vacina", label: "Tipo de vacina", required: true },
      { name: "antirrabica_ind", label: "Vacina antirrábica", type: "checkbox", required: true },
      { name: "fabricante", label: "Fabricante", required: true },
      { name: "lote", label: "Lote", required: true },
      { name: "data_vacina", label: "Data da aplicação", type: "date", required: true, defaultToday: true },
      { name: "dose_vacina", label: "Dose", required: true },
      { name: "via_aplicacao", label: "Via de aplicação", required: true },
      { name: "data_prox_dose", label: "Data da próxima dose", type: "date", required: true, defaultToday: true },
      { name: "validade_lote", label: "Validade do lote", type: "date", required: true, defaultToday: true },
      { name: "observ", label: "Observações", type: "textarea", required: true, full: true },
      {
        name: "situacao",
        label: "Situação",
        type: "select",
        required: true,
        options: [
          ["Agendada", "Agendada"],
          ["Aplicada", "Aplicada"],
          ["Cancelada", "Cancelada"],
        ],
      },
    ],
  },
};

const recordsByResource = Object.fromEntries(
  Object.keys(resourceConfig).map((resource) => [resource, []])
);
const offsets = Object.fromEntries(
  Object.keys(resourceConfig).map((resource) => [resource, 0])
);
const hasMore = Object.fromEntries(
  Object.keys(resourceConfig).map((resource) => [resource, true])
);
const referenceData = {
  tutores: [],
  especies: [],
  racas: [],
};
const referenceConfig = {
  tutores: {
    endpoint: "/api/tutores/",
    idField: "id_tutores",
    label: (record) => `${record.nome} ${record.sobrenome}`,
  },
  especies: {
    endpoint: "/api/especies/",
    idField: "id_especies",
    label: (record) => record.nome,
  },
  racas: {
    endpoint: "/api/racas/",
    idField: "id_racas",
    label: (record) => record.nome,
  },
};
let activeResource = "tutores";
let editingRecord = null;
let noticeTimer = null;

const notice = document.getElementById("notice");
const tableHead = document.getElementById("tableHead");
const tableBody = document.getElementById("tableBody");
const searchInput = document.getElementById("searchInput");
const dialog = document.getElementById("recordDialog");
const recordForm = document.getElementById("recordForm");
const formFields = document.getElementById("formFields");
const formError = document.getElementById("formError");
const saveButton = document.getElementById("saveButton");

function showNotice(type, message, persistent = false) {
  window.clearTimeout(noticeTimer);
  notice.className = `notice show ${type}`;
  notice.textContent = message;
  if (!persistent) {
    noticeTimer = window.setTimeout(() => {
      notice.className = "notice";
      notice.textContent = "";
    }, 6000);
  }
}

function getErrorMessage(data, status) {
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
    const field = data.detail[0].loc?.slice(-1)[0];
    return field ? `${field}: ${data.detail[0].msg}` : data.detail[0].msg;
  }
  if (status === 401) return "Sua sessão expirou. Entre novamente.";
  if (status === 403) return "Seu usuário não tem permissão para esta ação.";
  if (status === 404) return "O registro solicitado não foi encontrado.";
  if (status === 409) return "Já existe um registro com esses dados.";
  return "Não foi possível concluir a operação com a API.";
}

async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Não foi possível conectar à API VetQuick.");
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  if (!response.ok) {
    if (response.status === 401) {
      clearSession();
      window.location.replace("index.html");
    }
    throw new Error(getErrorMessage(data, response.status));
  }
  return data;
}

function clearSession() {
  [
    "vetquick_token",
    "vetquick_token_type",
    "vetquick_expires_in",
    "vetquick_veterinario",
    "vetquick_veterinario_id",
  ].forEach((key) => sessionStorage.removeItem(key));
}

function displayDate(value, includeTime = false) {
  if (!value) return "—";
  if (!includeTime && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return `${day}/${month}/${year}`;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat("pt-BR", includeTime
      ? { dateStyle: "short", timeStyle: "short" }
      : { dateStyle: "short" }).format(date);
}

function updateCounts() {
  Object.keys(resourceConfig).forEach((resource) => {
    document.getElementById(`count-${resource}`).textContent =
      String(recordsByResource[resource].length);
  });
}

function updatePageHeading() {
  const config = resourceConfig[activeResource];
  document.getElementById("pageTitle").textContent = config.title;
  document.getElementById("sectionTitle").textContent =
    `Registros de ${config.title.toLowerCase()}`;
  document.getElementById("sectionDescription").textContent = config.description;
  document.getElementById("createButton").innerHTML =
    `<span aria-hidden="true">+</span> Novo ${config.singular}`;
}

function formatCell(column, record) {
  if (column.primary) return record[column.primary] ?? "—";
  const value = record[column.field];
  if (value === null || value === undefined || value === "") return "—";
  if (column.format === "date") return displayDate(value);
  if (column.format === "datetime") return displayDate(value, true);
  if (column.format === "association") {
    const reference = referenceConfig[column.lookup];
    const associatedRecord = referenceData[column.lookup].find(
      (item) => String(item[reference.idField]) === String(value)
    );
    return associatedRecord
      ? `${reference.label(associatedRecord)} (ID ${value})`
      : `ID ${value}`;
  }
  if (column.format === "status") {
    return String(value).replaceAll("_", " ");
  }
  return `${value}${column.suffix || ""}`;
}

function renderTable() {
  const config = resourceConfig[activeResource];
  tableHead.replaceChildren();
  config.columns.forEach((column) => {
    const th = document.createElement("th");
    th.textContent = column.label;
    tableHead.append(th);
  });
  const actionsHeading = document.createElement("th");
  actionsHeading.textContent = "Ações";
  actionsHeading.className = "actions-heading";
  tableHead.append(actionsHeading);

  const query = searchInput.value.trim().toLocaleLowerCase("pt-BR");
  const records = recordsByResource[activeResource].filter((record) =>
    [
      ...Object.values(record),
      ...config.columns
        .filter((column) => column.format === "association")
        .map((column) => formatCell(column, record)),
    ].some((value) =>
      String(value ?? "").toLocaleLowerCase("pt-BR").includes(query)
    )
  );
  tableBody.replaceChildren();

  records.forEach((record) => {
    const row = document.createElement("tr");
    config.columns.forEach((column) => {
      const cell = document.createElement("td");
      if (column.primary) {
        const primary = document.createElement("span");
        primary.className = "record-name";
        primary.textContent = formatCell(column, record);
        cell.append(primary);
        const secondaryValue = column.secondaryPrefix
          ? `${column.secondaryPrefix}${record[column.secondary] ?? "—"}`
          : record[column.secondary] ?? "—";
        const secondary = document.createElement("span");
        secondary.className = "record-secondary";
        secondary.textContent = secondaryValue;
        cell.append(secondary);
      } else if (column.format === "status") {
        const pill = document.createElement("span");
        pill.className = "status-pill";
        pill.textContent = formatCell(column, record);
        cell.append(pill);
      } else {
        cell.textContent = formatCell(column, record);
      }
      row.append(cell);
    });

    const actions = document.createElement("td");
    const actionGroup = document.createElement("div");
    actionGroup.className = "row-actions";
    [
      { action: "edit", label: "Editar", className: "row-action" },
      { action: "delete", label: "Excluir", className: "row-action delete" },
    ].forEach(({ action, label, className }) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = className;
      button.dataset.action = action;
      button.dataset.recordId = String(record[config.idField]);
      button.textContent = label;
      actionGroup.append(button);
    });
    actions.append(actionGroup);
    row.append(actions);
    tableBody.append(row);
  });

  const emptyState = document.getElementById("emptyState");
  emptyState.hidden = records.length > 0;
  document.getElementById("resultsLabel").textContent = query
    ? `${records.length} resultado(s) nesta lista`
    : `${recordsByResource[activeResource].length} registro(s) carregado(s)`;
  const loadMore = document.getElementById("loadMoreButton");
  loadMore.hidden = !hasMore[activeResource] || Boolean(query);
  updateCounts();
}

async function loadRecords(resource, append = false) {
  const config = resourceConfig[resource];
  const skip = append ? offsets[resource] : 0;
  if (!append) {
    offsets[resource] = 0;
    hasMore[resource] = true;
  }
  const records = await apiRequest(
    `${config.endpoint}?skip=${skip}&limit=${PAGE_SIZE}`
  );
  if (!Array.isArray(records)) {
    throw new Error(`A API retornou uma lista inválida para ${config.title.toLowerCase()}.`);
  }
  recordsByResource[resource] = append
    ? [...recordsByResource[resource], ...records]
    : records;
  offsets[resource] = skip + records.length;
  hasMore[resource] = records.length === PAGE_SIZE;
  if (resource === activeResource) renderTable();
  else updateCounts();
}

async function loadAllRecords(endpoint) {
  const allRecords = [];
  let skip = 0;
  while (true) {
    const page = await apiRequest(`${endpoint}?skip=${skip}&limit=${PAGE_SIZE}`);
    if (!Array.isArray(page)) {
      throw new Error("A API retornou um catálogo inválido.");
    }
    allRecords.push(...page);
    if (page.length < PAGE_SIZE) return allRecords;
    skip += page.length;
  }
}

async function loadReferenceData() {
  const entries = await Promise.all(
    Object.entries(referenceConfig).map(async ([key, config]) => [
      key,
      await loadAllRecords(config.endpoint),
    ])
  );
  entries.forEach(([key, records]) => {
    referenceData[key] = records;
  });
}

function setActiveResource(resource) {
  if (!resourceConfig[resource]) return;
  activeResource = resource;
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.resource === resource);
  });
  searchInput.value = "";
  updatePageHeading();
  renderTable();
}

function localDateTimeValue(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 16);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function localDateValue() {
  const date = new Date();
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 10);
}

function makeFormField(field, record) {
  const wrapper = document.createElement("div");
  wrapper.className = `form-field${field.full ? " full-width" : ""}`;
  const id = `field-${field.name}`;

  if (field.type === "checkbox") {
    const checkLine = document.createElement("div");
    checkLine.className = "checkbox-field";
    const input = document.createElement("input");
    input.id = id;
    input.name = field.name;
    input.type = "checkbox";
    input.checked = Boolean(record?.[field.name]);
    const label = document.createElement("label");
    label.htmlFor = id;
    label.textContent = field.label;
    checkLine.append(input, label);
    wrapper.append(checkLine);
    return wrapper;
  }

  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = field.label;
  let input;
  if (field.type === "textarea") {
    input = document.createElement("textarea");
  } else if (field.type === "select") {
    input = document.createElement("select");
    if (field.optionSource) {
      populateReferenceSelect(input, field.optionSource, record?.[field.name], record?.especie);
    } else {
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Selecione uma opção";
      input.append(placeholder);
      field.options.forEach(([value, text]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = text;
        input.append(option);
      });
    }
  } else {
    input = document.createElement("input");
    input.type = field.type || "text";
  }
  input.id = id;
  input.name = field.name;
  input.required = Boolean(field.required);
  if (field.type === "number") input.step = "1";

  let value = record?.[field.name];
  if (field.type === "datetime-local") value = localDateTimeValue(value);
  if ((value === null || value === undefined || value === "") && field.defaultToday) {
    value = localDateValue();
  }
  if ((value === null || value === undefined || value === "") && field.defaultNow) {
    value = localDateTimeValue(new Date().toISOString());
  }
  if (field.type !== "select" || !field.optionSource) {
    input.value = value ?? "";
  }
  wrapper.append(label, input);
  return wrapper;
}

function populateReferenceSelect(select, source, selectedValue = "", speciesId = "") {
  const config = referenceConfig[source];
  const selected = selectedValue === null || selectedValue === undefined
    ? ""
    : String(selectedValue);
  let records = referenceData[source];
  if (source === "racas" && speciesId) {
    records = records.filter(
      (record) => String(record.especie_associada) === String(speciesId)
    );
  }

  select.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = `Selecione ${source === "tutores" ? "um tutor" : source === "especies" ? "uma espécie" : "uma raça"}`;
  select.append(placeholder);

  records.forEach((record) => {
    const id = String(record[config.idField]);
    const option = document.createElement("option");
    option.value = id;
    option.textContent = `${config.label(record)} · ID ${id}`;
    select.append(option);
  });

  if (selected && !records.some((record) => String(record[config.idField]) === selected)) {
    const option = document.createElement("option");
    option.value = selected;
    option.textContent = `ID ${selected} (nome indisponível)`;
    select.append(option);
  }
  select.value = selected;
}

function openRecordDialog(record = null) {
  editingRecord = record;
  const config = resourceConfig[activeResource];
  document.getElementById("dialogTitle").textContent =
    record ? `Editar ${config.singular}` : `Novo ${config.singular}`;
  saveButton.textContent = record ? "Salvar alterações" : "Salvar registro";
  formError.className = "form-error";
  formError.textContent = "";
  formFields.replaceChildren();
  config.fields.forEach((field) => formFields.append(makeFormField(field, record)));
  const speciesSelect = formFields.querySelector("#field-especie");
  const breedSelect = formFields.querySelector("#field-raca");
  if (speciesSelect && breedSelect) {
    speciesSelect.addEventListener("change", () => {
      populateReferenceSelect(breedSelect, "racas", "", speciesSelect.value);
    });
  }
  dialog.showModal();
}

function serializeForm() {
  const config = resourceConfig[activeResource];
  const formData = new FormData(recordForm);
  const payload = {};
  config.fields.forEach((field) => {
    const value = formData.get(field.name);
    if (field.type === "checkbox") {
      payload[field.name] = Boolean(value);
    } else if (value === null || value === "") {
      if (field.required) payload[field.name] = "";
    } else if (field.type === "number") {
      payload[field.name] = Number(value);
    } else if (field.optionSource) {
      payload[field.name] = Number(value);
    } else {
      payload[field.name] = String(value).trim();
    }
  });

  if (activeResource === "tutores") {
    payload.cadastroconfirmado = Boolean(editingRecord?.cadastroconfirmado);
  } else if (activeResource === "animais") {
    payload.vet_rfid_vinculo = Number(
      editingRecord?.vet_rfid_vinculo || veterinarianId
    );
  } else if (activeResource === "consultas" || activeResource === "vacinas") {
    payload.vet_responsavel = Number(
      editingRecord?.vet_responsavel || veterinarianId
    );
  }
  return payload;
}

async function saveRecord(event) {
  event.preventDefault();
  if (!recordForm.reportValidity()) return;

  const config = resourceConfig[activeResource];
  if (
    activeResource === "tutores" &&
    !recordForm.elements.cep.value.trim() &&
    !recordForm.elements.enderecoassociado.value.trim()
  ) {
    formError.className = "form-error show";
    formError.textContent = "Informe um CEP para localizar o endereço ou o ID de um endereço já cadastrado.";
    return;
  }

  const recordId = editingRecord?.[config.idField];
  const path = recordId === undefined
    ? config.endpoint
    : `${config.endpoint}${recordId}`;
  saveButton.disabled = true;
  saveButton.textContent = "Salvando...";
  formError.className = "form-error";
  formError.textContent = "";

  try {
    await apiRequest(path, {
      method: recordId === undefined ? "POST" : "PUT",
      body: JSON.stringify(serializeForm()),
    });
    dialog.close();
    try {
      await Promise.all([
        loadRecords(activeResource),
        ...(activeResource === "tutores" ? [loadReferenceData()] : []),
      ]);
      showNotice("success", `${config.singular[0].toUpperCase()}${config.singular.slice(1)} ${recordId === undefined ? "cadastrado" : "atualizado"} com sucesso.`);
    } catch (refreshError) {
      showNotice("error", `Registro salvo, mas a lista não pôde ser atualizada: ${refreshError.message}`);
    }
  } catch (error) {
    formError.className = "form-error show";
    formError.textContent = error.message;
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = recordId === undefined ? "Salvar registro" : "Salvar alterações";
  }
}

async function deleteRecord(recordId) {
  const config = resourceConfig[activeResource];
  if (!window.confirm(`Tem certeza que deseja excluir este ${config.singular}?`)) return;
  try {
    await apiRequest(`${config.endpoint}${recordId}`, { method: "DELETE" });
    showNotice("success", `${config.singular[0].toUpperCase()}${config.singular.slice(1)} excluído com sucesso.`);
    await Promise.all([
      loadRecords(activeResource),
      ...(activeResource === "tutores" ? [loadReferenceData()] : []),
    ]);
  } catch (error) {
    showNotice("error", error.message);
  }
}

async function initializeDashboard() {
  if (!token || !veterinarianId) {
    window.location.replace("index.html");
    return;
  }

  try {
    const profile = await apiRequest("/api/auth/me");
    sessionStorage.setItem("vetquick_veterinario", JSON.stringify(profile));
    const email = profile.email || "Sessão autenticada";
    document.getElementById("profileEmail").textContent = email;
    document.getElementById("profileAvatar").textContent = email.slice(0, 1).toUpperCase();
    await Promise.all([
      loadReferenceData(),
      ...Object.keys(resourceConfig).map((resource) => loadRecords(resource)),
    ]);
    setActiveResource(activeResource);
  } catch (error) {
    showNotice("error", error.message, true);
  }
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => setActiveResource(button.dataset.resource));
});

document.getElementById("createButton").addEventListener("click", () => openRecordDialog());
document.getElementById("refreshButton").addEventListener("click", async () => {
  try {
    await loadRecords(activeResource);
    showNotice("success", "Lista atualizada.");
  } catch (error) {
    showNotice("error", error.message);
  }
});
document.getElementById("loadMoreButton").addEventListener("click", async () => {
  try {
    await loadRecords(activeResource, true);
  } catch (error) {
    showNotice("error", error.message);
  }
});
searchInput.addEventListener("input", renderTable);
tableBody.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const config = resourceConfig[activeResource];
  const record = recordsByResource[activeResource].find(
    (item) => String(item[config.idField]) === button.dataset.recordId
  );
  if (!record) return;
  if (button.dataset.action === "edit") openRecordDialog(record);
  if (button.dataset.action === "delete") deleteRecord(button.dataset.recordId);
});
recordForm.addEventListener("submit", saveRecord);
document.getElementById("closeDialogButton").addEventListener("click", () => dialog.close());
document.getElementById("cancelDialogButton").addEventListener("click", () => dialog.close());
document.getElementById("logoutButton").addEventListener("click", () => {
  clearSession();
  window.location.replace("index.html");
});

initializeDashboard();
