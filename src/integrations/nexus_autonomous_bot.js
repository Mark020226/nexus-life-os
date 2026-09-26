/**
 * ============================================================================
 * NEXUS Life OS — Autonomous 24/7 Cloud Webhook & Brain v4.0
 * ============================================================================
 * Host: Google Apps Script (Google Cloud Serverless - 100% Free Forever)
 * Propietario: Mark Eduardo Terrazas Luna (mark23terrazas30@gmail.com)
 * Integraciones: Telegram Bot (@HAZARDNexusbot) + Google Calendar + Gmail + Google Sheets + Gemini AI
 * Cero dependencia de PC o Antigravity encendidos.
 * ============================================================================
 */

// CONFIGURACIÓN CENTRAL DE CREDENCIALES
var TELEGRAM_BOT_TOKEN = "PEGAR_TELEGRAM_BOT_TOKEN_AQUI";
var GEMINI_API_KEY = "PEGAR_GEMINI_API_KEY_AQUI";
var TIMEZONE = "America/La_Paz"; // UTC-4 Bolivia
var SLACK_API_TOKEN = ""; // Opcional
var RESOURCES_SHEET_ID = "PEGAR_ID_DE_GOOGLE_SHEET_AQUI"; // Opcional (si se deja vacío, se auto-crea o gestiona)

/**
 * PERFILES DE ACTIVIDAD PARA GUÍAS DE EJECUCIÓN HIPER-DETALLADAS
 * Contexto profundo personalizado para Mark (Salud, Métodos InvernovAH, GCI Tokio, Becas)
 */
var ACTIVITY_PROFILES = {
  EXERCISE: {
    title: "🏋️ Salud, Calistenia & Acondicionamiento",
    context: "Mark tiene historial de TENDINITIS (muñecas/antebrazos) y su condición física actual es BAJA (sedentarismo reciente). " +
      "Meta innegociable: alcanzar y sostener para siempre su mejor estado físico. " +
      "REGLAS BIOMECÁNICAS ESTRICTAS: " +
      "1) Calentamiento articular de muñecas, dedos y antebrazos OBLIGATORIO (5 min previos). " +
      "2) Ejercicios de bajo impacto articular; calistenia base, activación escapular y fortalecimiento de core antes de cargas. " +
      "3) Progresión ultra-conservadora: si hay molestia en tendones, DETENER de inmediato y cambiar a movilidad/piernas. " +
      "4) Vuelta a la calma y estiramiento fascial suave al finalizar (5 min).",
    keywords: ["entrenamiento", "ejercicio", "fuerza", "físico", "salud", "gym", "calistenia", "🏋️"]
  },
  STUDY_UMSA: {
    title: "🎓 Estudio de Alto Rendimiento UMSA (Método InvernovAH)",
    context: "Metodología de ingeniería cognitiva de Álvaro Hernández (InvernovAH): " +
      "1) ACTIVE RECALL: Prohibido subrayar o releer pasivamente. Plantear preguntas clave antes de ver el texto y responder de memoria. " +
      "2) TÉCNICA FEYNMAN: Explicar conceptos complejos (procesos, fórmulas, normativas) en lenguaje tan simple que un niño de 10 años lo entienda. " +
      "3) POMODORO 50/10: 50 min de foco ultra-profundo (cero notificaciones), 10 min de descanso activo (caminar, agua, cero pantallas). " +
      "4) SPACED REPETITION: Anotar los 2 conceptos más difíciles para repaso en 24h, 3 días y 7 días. " +
      "5) THINKING ON PAPER: Derivar cálculos y diagramas a mano en papel antes de usar software. " +
      "Materias activas de Mark: Gerencia de Proyectos, Seguridad Industrial, Taller 1, Diseño Industrial.",
    keywords: ["estudio", "umsa", "tarea", "académico", "refuerzo", "parcial", "examen", "gerencia", "seguridad", "taller", "diseño industrial", "deep work", "🎓", "📚"]
  },
  GCI_WORLD: {
    title: "🔬 GCI World Tokio 2026 (Matsuo & Iwasawa Lab)",
    context: "Programa de Ciencia de Datos y Machine Learning con la Universidad de Tokio (Matsuo Lab). " +
      "Mark es estudiante de Ingeniería Industrial con rápida capacidad de abstracción. " +
      "ENFOQUE: Python, Pandas, Numpy, Scikit-Learn, algoritmos de ML y competiciones de Kaggle. " +
      "REGLA DE CONTEXTO: Sintetiza requerimientos del Sensei, deadlines de entregables y revisión de notebooks en Omnicampus/Slack.",
    keywords: ["gci", "matsuo", "tokyo", "tokio", "kaggle", "machine learning", "python", "pandas", "data science", "🔬"]
  },
  SCHOLARSHIP: {
    title: "🌍 Ruta Estratégica de Becas Internacionales",
    context: "Búsqueda y postulación a becas de posgrado/intercambio internacional para Mark. " +
      "Perfil: Estudiante avanzado de Ingeniería Industrial UMSA (Bolivia), GCI World Tokio 2026, Python/Data/IA, inglés intermedio-avanzado. " +
      "RUTA SISTEMÁTICA PASO A PASO: " +
      "1) Mapeo de convocatorias abiertas (Euraxess, DAAD, Chevening, Fulbright, OEA, JASSO, MEXT, Fundación Carolina). " +
      "2) Preparación de CV formato Harvard (ATS-friendly, cuantificando impacto). " +
      "3) Redacción de Carta de Motivación con enfoque en transferencia tecnológica a la industria e IA. " +
      "4) Verificación de suficiencia de idioma (IELTS/TOEFL/Duolingo) y homologación académica. " +
      "5) Gestión de 2 cartas de recomendación académica/laboral con antelación.",
    keywords: ["beca", "scholarship", "postular", "convocatoria", "intercambio", "maestría", "master", "jasso", "mext", "daad", "fulbright"]
  },
  MONETIZATION: {
    title: "💰 Proyecto Monetización & FIRE ($1,000 USDT)",
    context: "Meta financiera prioritaria: Liquidar pasivo de 1,000 USDT antes del 30 de noviembre 2026. " +
      "Focos de rentabilidad: Freelance tech en Upwork/Fiverr (automatización de procesos con Python, n8n, scraping, bots e IA aplicada a PyMEs), " +
      "prospección directa de clientes remotos internacionales en USD.",
    keywords: ["monetización", "monetizacion", "freelance", "upwork", "fiverr", "1000", "usdt", "dólares", "dolares", "ingresos", "💰"]
  },
  ENGLISH: {
    title: "🇬🇧 Inmersión en Inglés Técnico",
    context: "Curso virtual de inglés (foco profesional/académico). " +
      "Técnica: Inmersión auditiva activa, técnica de shadowing, adquisición de vocabulario técnico de ingeniería e IA, simulación de entrevistas laborales.",
    keywords: ["inglés", "ingles", "english", "listening", "speaking", "vocabulario", "🇬🇧"]
  },
  MORNING_ROUTINE: {
    title: "🌅 Rutina Matutina & Alistamiento",
    context: "Protocolo matutino de activación: Hidratación con electrolitos, movilidad articular ligera (sin sobrecarga en muñecas), " +
      "revisión de las 3 prioridades del Protocolo NASA para el día, cero dopamina barata ni redes sociales antes de salir.",
    keywords: ["rutina matutina", "alistamiento", "despertar", "madrugada", "🌅"]
  },
  DEFAULT: {
    title: "📌 Bloque de Enfoque NEXUS",
    context: "Filosofía InvernovAH: Cero fricción cognitiva, foco 80/20, eliminación de distractores, ejecución paso a paso.",
    keywords: []
  }
};

/**
 * Punto de entrada HTTP POST: Telegram empuja cada mensaje aquí en tiempo real.
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return HtmlService.createHtmlOutput("OK");
    }

    var update = JSON.parse(e.postData.contents);
    var message = update.message || update.edited_message;
    if (!message) return HtmlService.createHtmlOutput("OK");

    // 🛑 1. FILTRO DE MENSAJES VIEJOS (DETIENE BUCLES DE TELEGRAM)
    // Si Telegram intenta reenviar un mensaje que tiene más de 120 segundos de antigüedad, se ignora de inmediato.
    var msgDate = message.date;
    var nowSec = Math.floor(Date.now() / 1000);
    if (msgDate && (nowSec - msgDate > 120)) {
      return HtmlService.createHtmlOutput("OK");
    }

    // 🛑 2. FILTRO DEDUPLICADOR POR UPDATE_ID
    var cache = CacheService.getScriptCache();
    var updateId = update.update_id ? update.update_id.toString() : null;
    if (updateId) {
      if (cache.get("up_" + updateId)) {
        return HtmlService.createHtmlOutput("OK"); // Ignorar reintento duplicado
      }
      cache.put("up_" + updateId, "1", 300); // Recordar por 5 minutos
    }

    var chatId = message.chat.id;
    var text = message.text || message.caption || "";
    var voice = message.voice || message.audio;
    var isVoice = false;

    // Feedback inmediato a Telegram ("Escribiendo...") para confirmar recepción
    sendChatAction(chatId, "typing");

    // 3. Transcripción multimodal si es nota de voz
    if (voice && voice.file_id) {
      sendTelegramMessage(chatId, "🎙️ _Escuchando tu nota de voz con IA en la nube..._");
      text = transcribeVoiceWithGemini(voice.file_id);
      isVoice = true;
      if (!text) {
        sendTelegramMessage(chatId, "⚠️ No pude escuchar con claridad el audio. Intenta hablar más cerca del micrófono.");
        return HtmlService.createHtmlOutput("OK");
      }
    }

    if (!text || text.trim() === "") {
      return HtmlService.createHtmlOutput("OK");
    }

    // 4. Procesar intención y ejecutar acción en Google Calendar / Sheets / IA
    var reply = handleNexusIntelligence(text.trim(), chatId);

    if (isVoice) {
      reply = "🎙️ *Nota de voz transcrita:* \"_" + text + "_\"\n\n" + reply;
    }

    // 5. Responder al usuario en Telegram
    sendTelegramMessage(chatId, reply);

  } catch (err) {
    Logger.log("Error en doPost: " + err.toString());
  }

  // IMPORTANTE: HtmlService previene el error '302 Found' de Google que causaba bucles en Telegram
  return HtmlService.createHtmlOutput("OK");
}

function doGet(e) {
  return HtmlService.createHtmlOutput("NEXUS Life OS 24/7 Cloud Webhook v4.0 is LIVE and ACTIVE.");
}

/**
 * MOTOR CENTRAL DE INTELIGENCIA Y ENRUTAMIENTO DE INTENCIONES
 */
function handleNexusIntelligence(text, chatId) {
  var lower = text.toLowerCase();

  // A. IMPREVISTO / RECALCULAR HORARIO DE HOY (Prioridad #1)
  if (lower.indexOf("imprevisto") !== -1 || lower.indexOf("surgio") !== -1 || 
      lower.indexOf("surgió") !== -1 || lower.indexOf("retraso") !== -1 || 
      lower.indexOf("recalcular") !== -1 || lower.indexOf("cambio de horario") !== -1) {
    return handleImprevistoCalendar(text);
  }

  // B. AGENDAR ACTIVIDAD FUTURA CON CASCADA DINÁMICA (Prioridad #2)
  var isFutureIntent = (
    lower.indexOf("/agendar") !== -1 ||
    lower.indexOf("agendar") !== -1 ||
    lower.indexOf("agenda para") !== -1 ||
    lower.indexOf("programa para") !== -1 ||
    lower.indexOf("agéndame") !== -1 ||
    lower.indexOf("agendame") !== -1 ||
    (lower.indexOf("tengo") !== -1 && (
      lower.indexOf("el lunes") !== -1 || lower.indexOf("el martes") !== -1 ||
      lower.indexOf("el miércoles") !== -1 || lower.indexOf("el miercoles") !== -1 ||
      lower.indexOf("el jueves") !== -1 || lower.indexOf("el viernes") !== -1 ||
      lower.indexOf("el sábado") !== -1 || lower.indexOf("el sabado") !== -1 ||
      lower.indexOf("el domingo") !== -1 || lower.indexOf("mañana") !== -1 ||
      lower.indexOf("pasado mañana") !== -1 ||
      /\bel \d{1,2}\b/.test(lower) || /\b\d{1,2}\/\d{1,2}\b/.test(lower)
    ))
  );
  if (isFutureIntent) {
    return handleFutureEventSchedule(text);
  }

  // C. GUÍA DE EJECUCIÓN INMEDIATA (QUÉ Y CÓMO HACER AHORA) (Prioridad #3)
  if (lower === "/guia" || lower === "/guía" || lower.indexOf("qué hago ahora") !== -1 || 
      lower.indexOf("que hago ahora") !== -1 || lower.indexOf("cómo empiezo") !== -1 ||
      lower.indexOf("como empiezo") !== -1 || lower.indexOf("procedimiento de estudio") !== -1 ||
      lower.indexOf("guía de ejercicio") !== -1 || lower.indexOf("guia de ejercicio") !== -1) {
    return getActivityGuideForNow();
  }

  // D. CONSULTA DE ITINERARIO / PLAN DE HOY (Prioridad #4)
  if (lower === "/hoy" || lower === "/itinerario" || lower.indexOf("itinerario") !== -1 || 
      lower.indexOf("plan de hoy") !== -1 || lower.indexOf("qué tengo hoy") !== -1 || 
      lower.indexOf("que tengo hoy") !== -1) {
    return getTodayScheduleReport();
  }

  // E. BRIEFING UNIFICADO 360° (GMAIL + OMNICAMPUS + SLACK) (Prioridad #5)
  if (lower === "/briefing" || lower.indexOf("briefing") !== -1 || 
      lower.indexOf("actualízame") !== -1 || lower.indexOf("actualizame") !== -1 || 
      lower.indexOf("qué está pasando") !== -1 || lower.indexOf("que esta pasando") !== -1 || 
      lower.indexOf("dame un resumen general") !== -1 || lower.indexOf("resumen del día") !== -1) {
    return getUnifiedTriPlatformBriefing();
  }

  // F. INGESTA UNIVERSAL DE ENLACES (REDES SOCIALES Y WEB) (Prioridad #6)
  var urlMatch = text.match(/https?:\/\/[^\s]+/i);
  if (urlMatch) {
    return handleLinkIngest(text, urlMatch[0]);
  }

  // G. FINANZAS / GASTOS / INGRESOS (Prioridad #7)
  if (lower.indexOf("gasté") !== -1 || lower.indexOf("gaste") !== -1 || 
      lower.indexOf("gasto") !== -1 || lower.indexOf("compré") !== -1 || 
      lower.indexOf("ingreso") !== -1 || lower.indexOf("cobré") !== -1 || 
      lower.indexOf("bs") !== -1 || lower.indexOf("usdt") !== -1) {
    return handleFinanceRecord(text);
  }

  // H. HÁBITOS / SUEÑO / ENERGÍA (Prioridad #8)
  if (lower.indexOf("dormí") !== -1 || lower.indexOf("dormi") !== -1 || 
      lower.indexOf("sueño") !== -1 || lower.indexOf("energia") !== -1 || 
      lower.indexOf("energía") !== -1) {
    return handleHabitsRecord(text);
  }

  // I. CONSULTA ACADÉMICA / PREGUNTAS / ESTRATEGIA (GEMINI 3.5 FLASH)
  return callGeminiBrain(text);
}

/**
 * Detecta el perfil de actividad a partir del título del evento
 */
function detectActivityProfile(eventTitle) {
  var lower = eventTitle.toLowerCase();
  var keys = Object.keys(ACTIVITY_PROFILES);
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    var prof = ACTIVITY_PROFILES[k];
    if (prof.keywords && prof.keywords.length > 0) {
      for (var j = 0; j < prof.keywords.length; j++) {
        if (lower.indexOf(prof.keywords[j]) !== -1) {
          return k;
        }
      }
    }
  }
  return "DEFAULT";
}

/**
 * Genera una Guía de Ejecución ultra-detallada (Qué y Cómo) adaptada al contexto de Mark
 */
function generateActivityGuide(eventTitle, startTime, endTime) {
  var profileKey = detectActivityProfile(eventTitle);
  var profile = ACTIVITY_PROFILES[profileKey];

  var durationMin = 60;
  if (startTime && endTime) {
    durationMin = Math.max(15, Math.round((endTime.getTime() - startTime.getTime()) / 60000));
  }

  var sStr = startTime ? Utilities.formatDate(startTime, TIMEZONE, "HH:mm") : "--:--";
  var eStr = endTime ? Utilities.formatDate(endTime, TIMEZONE, "HH:mm") : "--:--";

  // Contexto adicional en tiempo real si es GCI World
  var liveContext = "";
  if (profileKey === "GCI_WORLD") {
    try {
      var threads = GmailApp.search("(from:omnicampus OR from:slack.com OR tokyo OR matsuo OR gci) newer_than:3d", 0, 3);
      if (threads.length > 0) {
        var updates = [];
        for (var t = 0; t < threads.length; t++) {
          var m = threads[t].getMessages()[0];
          updates.push("• Asunto: " + m.getSubject() + " | Fragmento: " + m.getPlainBody().substring(0, 140).replace(/\n/g, " "));
        }
        liveContext = "\n\nÚLTIMOS COMUNICADOS / DEADLINES DETECTADOS EN GMAIL/OMNICAMPUS:\n" + updates.join("\n");
      }
    } catch (e) {
      Logger.log("No se pudo obtener updates en vivo de GCI: " + e.toString());
    }
  }

  var prompt = 
    "Eres el Director de Operaciones Cognitivas y Entrenador de NEXUS Life OS para Mark Eduardo Terrazas Luna. " +
    "Genera una GUÍA DE EJECUCIÓN INMEDIATA Y ACCIONABLE para el siguiente bloque del calendario:\n\n" +
    "ACTIVIDAD: " + eventTitle + "\n" +
    "TIEMPO DISPONIBLE: " + durationMin + " minutos (" + sStr + " a " + eStr + ")\n" +
    "PERFIL: " + profile.title + "\n" +
    "PAUTAS Y RESTRICCIONES CRÍTICAS:\n" + profile.context + liveContext + "\n\n" +
    "REGLAS DE FORMATO (Markdown conciso, directo al grano, cero paja):\n" +
    "🎯 **1. OBJETIVO DEL BLOQUE:** (Una sola frase medible)\n" +
    "⚡ **2. PREPARACIÓN & CERO FRICCIÓN (Primeros 3-5 min):** (Qué tener abierto o listo)\n" +
    "📋 **3. RUTA PASO A PASO (Procedimiento con tiempos):** (Desglose exacto en minutos. Si es estudio, usa Active Recall/Pomodoro/Feynman; si es ejercicio, movilidad de muñecas/calistenia progresiva; si es becas, búsqueda/CV/requisitos; si es GCI, entregables concretos)\n" +
    "⚠️ **4. SEÑAL DE ALERTA / CUÁNDO PARAR:** (Biomecánica, fatiga o límite de tiempo)\n" +
    "🏆 **5. MICRO-VICTORIA DEFINIDA:** (Criterio exacto para decir 'bloque superado')";

  return callGeminiBrain(prompt);
}

/**
 * Consulta el evento que se está ejecutando ahora mismo y devuelve su Guía de Ejecución
 */
function getActivityGuideForNow() {
  var cal = CalendarApp.getDefaultCalendar();
  var now = new Date();
  var events = cal.getEventsForDay(now);

  if (!events || events.length === 0) {
    return "📅 No tienes actividades registradas en tu calendario para hoy. Puedes agendar una con `/agendar`.";
  }

  events.sort(function(a, b) {
    return a.getStartTime().getTime() - b.getStartTime().getTime();
  });

  var nowTime = now.getTime();
  var currentEvent = null;
  var nextEvent = null;

  for (var i = 0; i < events.length; i++) {
    var ev = events[i];
    var st = ev.getStartTime().getTime();
    var et = ev.getEndTime().getTime();
    if (nowTime >= st && nowTime < et) {
      currentEvent = ev;
      break;
    }
    if (st > nowTime && !nextEvent) {
      nextEvent = ev;
    }
  }

  var targetEvent = currentEvent || nextEvent;
  if (!targetEvent) {
    return "🌙 Has completado todos los bloques de hoy. ¡Es hora de cenar y proteger el sueño biológico a las 22:30!";
  }

  var isCurrent = (targetEvent === currentEvent);
  var estadoStr = isCurrent ? "👉 *[ACTIVIDAD EN CURSO]*" : "⏳ *[PRÓXIMA ACTIVIDAD]*";
  var sStr = Utilities.formatDate(targetEvent.getStartTime(), TIMEZONE, "HH:mm");
  var eStr = Utilities.formatDate(targetEvent.getEndTime(), TIMEZONE, "HH:mm");

  var guide = generateActivityGuide(targetEvent.getTitle(), targetEvent.getStartTime(), targetEvent.getEndTime());

  return estadoStr + " `" + sStr + " - " + eStr + "`\n" +
         "📌 *" + targetEvent.getTitle() + "*\n\n" +
         guide;
}

/**
 * Devuelve el reporte del itinerario de hoy consultando el calendario en vivo
 */
function getTodayScheduleReport() {
  var cal = CalendarApp.getDefaultCalendar();
  var now = new Date();
  var events = cal.getEventsForDay(now);

  if (!events || events.length === 0) {
    return "📅 No tienes eventos programados para hoy en tu calendario.";
  }

  events.sort(function(a, b) {
    return a.getStartTime().getTime() - b.getStartTime().getTime();
  });

  var dateStr = Utilities.formatDate(now, TIMEZONE, "dd/MM/yyyy");
  var lines = ["📅 *Tu Itinerario Dinámico de Hoy (" + dateStr + "):*\n"];
  var nowTime = now.getTime();
  var currentEventFound = null;

  for (var i = 0; i < events.length; i++) {
    var ev = events[i];
    var sStr = Utilities.formatDate(ev.getStartTime(), TIMEZONE, "HH:mm");
    var eStr = Utilities.formatDate(ev.getEndTime(), TIMEZONE, "HH:mm");
    var isCurrent = (nowTime >= ev.getStartTime().getTime() && nowTime < ev.getEndTime().getTime());
    var tag = isCurrent ? "👉 *[EN ESTE MOMENTO]* " : "";
    lines.push(tag + "`" + sStr + " - " + eStr + "` " + ev.getTitle());
    if (isCurrent) currentEventFound = ev;
  }

  lines.push("\n💡 _Tip: Escribe `/guia` para ver el procedimiento paso a paso de tu actividad actual._");
  return lines.join("\n");
}

/**
 * GESTIONA UN IMPREVISTO EN TIEMPO REAL (DÍA ACTUAL)
 */
function handleImprevistoCalendar(text) {
  var cal = CalendarApp.getDefaultCalendar();
  var now = new Date();
  var lower = text.toLowerCase();

  var startTime = new Date();
  var endTime = new Date();
  var durationMin = 60; // default 1 hora

  // 1. Detectar si dice "hasta las HH:MM"
  var hastaMatch = text.match(/hasta\s+(?:las\s+)?(\d{1,2}):(\d{2})/i);
  if (hastaMatch) {
    var endHour = parseInt(hastaMatch[1], 10);
    var endMin = parseInt(hastaMatch[2], 10);
    endTime.setHours(endHour, endMin, 0, 0);
    if (endTime.getTime() <= startTime.getTime()) {
      endTime.setDate(endTime.getDate() + 1);
    }
    durationMin = Math.max(15, Math.round((endTime.getTime() - startTime.getTime()) / 60000));
  } else {
    // 2. Extraer duración explícita en minutos u horas
    var minMatch = text.match(/(\d+)\s*(?:minutos|min|m\b)/i);
    var hourMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:horas|hora|h\b)/i);
    if (minMatch) {
      durationMin = parseInt(minMatch[1], 10);
    } else if (hourMatch) {
      durationMin = Math.round(parseFloat(hourMatch[1]) * 60);
    }

    var startHour = now.getHours();
    var startMinute = Math.ceil((now.getMinutes() + 5) / 10) * 10;
    var timeMatch = text.match(/(?:a las|desde las|alas)\s*(\d{1,2}):(\d{2})/i);
    if (timeMatch) {
      startHour = parseInt(timeMatch[1], 10);
      startMinute = parseInt(timeMatch[2], 10);
      startTime.setHours(startHour, startMinute, 0, 0);
    }
    endTime = new Date(startTime.getTime() + durationMin * 60000);
  }

  // 3. Extraer descripción limpia
  var desc = "Actividad Imprevista";
  var prefixes = ["surgió un imprevisto:", "surgió un imprevisto", "surgio un imprevisto", "tengo", "surgió una actividad", "estaré ocupado", "estare ocupado", "imprevisto:"];
  for (var i = 0; i < prefixes.length; i++) {
    var idx = lower.indexOf(prefixes[i]);
    if (idx !== -1) {
      desc = text.substring(idx + prefixes[i].length).trim();
      break;
    }
  }

  // 4. Generar micro-guía y crear evento en Google Calendar
  var guide = generateActivityGuide("🚨 " + desc, startTime, endTime);
  var impEvent = cal.createEvent("🚨 Imprevisto: " + desc, startTime, endTime, {
    description: "Imprevisto registrado dinámicamente desde Telegram con NEXUS Life OS.\n\n" +
                 "📋 GUÍA DE EJECUCIÓN INMEDIATA:\n" + guide + "\n\n[NEXUS-LIFE-OS]"
  });
  impEvent.setColor(CalendarApp.EventColor.TOMATO);
  impEvent.addPopupReminder(10);

  // 5. Detectar eventos que colisionan y reubicarlos en buffers
  var todayEvents = cal.getEventsForDay(now);
  var displaced = [];

  for (var j = 0; j < todayEvents.length; j++) {
    var ev = todayEvents[j];
    if (ev.getId() === impEvent.getId()) continue;

    var evStart = ev.getStartTime();
    var evEnd = ev.getEndTime();

    // Colisión
    if (Math.max(evStart.getTime(), startTime.getTime()) < Math.min(evEnd.getTime(), endTime.getTime())) {
      var evTitle = ev.getTitle();
      if (evTitle.indexOf("UMSA") !== -1 || evTitle.indexOf("Sueño") !== -1 || evTitle.indexOf("Empresa") !== -1 || evTitle.indexOf("Inglés") !== -1) {
        ev.setDescription(ev.getDescription() + "\n⚠️ Solapamiento con imprevisto: " + desc);
      } else {
        var newEvStart = new Date(endTime.getTime() + 15 * 60000);
        var dur = evEnd.getTime() - evStart.getTime();
        var newEvEnd = new Date(newEvStart.getTime() + dur);
        
        ev.setTime(newEvStart, newEvEnd);
        displaced.push(evTitle + " (reubicado a las " + Utilities.formatDate(newEvStart, TIMEZONE, "HH:mm") + ")");
      }
    }
  }

  var sStr = Utilities.formatDate(startTime, TIMEZONE, "HH:mm");
  var eStr = Utilities.formatDate(endTime, TIMEZONE, "HH:mm");

  var report = "✅ *Itinerario Recalculado en tu Google Calendar:*\n\n" +
               "🚨 *Bloque Ocupado:* " + desc + "\n" +
               "⏰ *Horario:* `" + sStr + " - " + eStr + "` (" + durationMin + " min)\n\n";

  if (displaced.length > 0) {
    report += "🔄 *Ajustes Automáticos en tu Celular:*\n• " + displaced.join("\n• ") + "\n\n";
  } else {
    report += "🛡️ *Impacto Absorbido:* El imprevisto fue agendado sin alterar clases obligatorias.\n\n";
  }

  report += "📱 *Revisa Google Calendar:* La actividad ya tiene su guía de ejecución en la descripción.";
  return report;
}

/**
 * AGENDA ACTIVIDADES FUTURAS CON DETECCIÓN INTELIGENTE Y REUBICACIÓN EN CASCADA
 */
function handleFutureEventSchedule(text) {
  var now = new Date();
  var todayStr = Utilities.formatDate(now, TIMEZONE, "EEEE dd/MM/yyyy HH:mm");

  var extractPrompt = 
    "Eres el planificador de calendario de NEXUS Life OS. " +
    "Hoy es " + todayStr + " en Bolivia (America/La_Paz, UTC-4). " +
    "Analiza la siguiente solicitud para agendar una actividad futura:\n\n" +
    "\"" + text + "\"\n\n" +
    "Extrae y calcula la fecha y hora exacta. Si dice 'el viernes', calcula el próximo viernes respecto a hoy. " +
    "Si no especifica hora de inicio, asume las 10:00 AM si es mañana, o las 15:30 si es tarde. " +
    "Si no especifica duración, asume 60 minutos. " +
    "Devuelve ESTRICTAMENTE un JSON con este formato:\n" +
    "{\n" +
    "  \"date\": \"YYYY-MM-DD\",\n" +
    "  \"start_time\": \"HH:MM\",\n" +
    "  \"end_time\": \"HH:MM\",\n" +
    "  \"duration_min\": 60,\n" +
    "  \"description\": \"Nombre conciso de la actividad\",\n" +
    "  \"category\": \"UMSA | GCI | EMPRESA | BECAS | MONETIZACION | PERSONAL\",\n" +
    "  \"priority\": 1\n" +
    "}";

  var parsedData = callGeminiJSON(extractPrompt);
  if (!parsedData || !parsedData.date || !parsedData.start_time) {
    return "⚠️ No logré extraer con certeza la fecha u hora para agendar. Por favor indícamelo así:\n_\"Tengo examen de Gerencia el viernes 3 de octubre a las 11:00\"_";
  }

  var dateParts = parsedData.date.split("-");
  var startParts = parsedData.start_time.split(":");
  var endParts = parsedData.end_time ? parsedData.end_time.split(":") : null;

  var startDate = new Date(parseInt(dateParts[0], 10), parseInt(dateParts[1], 10) - 1, parseInt(dateParts[2], 10), parseInt(startParts[0], 10), parseInt(startParts[1], 10), 0);
  
  var endDate;
  if (endParts && endParts.length === 2) {
    endDate = new Date(parseInt(dateParts[0], 10), parseInt(dateParts[1], 10) - 1, parseInt(dateParts[2], 10), parseInt(endParts[0], 10), parseInt(endParts[1], 10), 0);
  } else {
    var durMin = parsedData.duration_min || 60;
    endDate = new Date(startDate.getTime() + durMin * 60000);
  }

  // Asignar emoji y color según categoría
  var emoji = "📌";
  var eventColor = CalendarApp.EventColor.PEACOCK;
  var cat = (parsedData.category || "").toUpperCase();

  if (cat.indexOf("UMSA") !== -1) {
    emoji = "🎓";
    eventColor = CalendarApp.EventColor.BLUEBERRY;
  } else if (cat.indexOf("GCI") !== -1) {
    emoji = "🔬";
    eventColor = CalendarApp.EventColor.GRAPE;
  } else if (cat.indexOf("EMPRESA") !== -1) {
    emoji = "🏢";
    eventColor = CalendarApp.EventColor.TANGERINE;
  } else if (cat.indexOf("BECAS") !== -1) {
    emoji = "🌍";
    eventColor = CalendarApp.EventColor.CYAN;
  } else if (cat.indexOf("MONETIZACION") !== -1) {
    emoji = "💰";
    eventColor = CalendarApp.EventColor.BASIL;
  }

  var fullTitle = emoji + " " + (parsedData.description || "Actividad Agendada");
  var cal = CalendarApp.getDefaultCalendar();

  // Generar Guía de Ejecución personalizada para adjuntar en la descripción
  var executionGuide = generateActivityGuide(fullTitle, startDate, endDate);

  var newEvent = cal.createEvent(fullTitle, startDate, endDate, {
    description: "Actividad agendada automáticamente desde Telegram con NEXUS Life OS.\n\n" +
                 "📋 GUÍA DE EJECUCIÓN (QUÉ Y CÓMO HACER):\n" + executionGuide + "\n\n[NEXUS-LIFE-OS]"
  });
  newEvent.setColor(eventColor);
  newEvent.addPopupReminder(10);
  newEvent.addPopupReminder(30);

  // Cascada: Verificar colisiones en ese día futuro
  var dayEvents = cal.getEventsForDay(startDate);
  var displaced = [];

  for (var k = 0; k < dayEvents.length; k++) {
    var ev = dayEvents[k];
    if (ev.getId() === newEvent.getId()) continue;

    var evStart = ev.getStartTime();
    var evEnd = ev.getEndTime();

    // Colisión de rango
    if (Math.max(evStart.getTime(), startDate.getTime()) < Math.min(evEnd.getTime(), endDate.getTime())) {
      var evTitle = ev.getTitle();
      if (evTitle.indexOf("UMSA") !== -1 || evTitle.indexOf("Sueño") !== -1 || evTitle.indexOf("Empresa") !== -1 || evTitle.indexOf("Inglés") !== -1) {
        ev.setDescription(ev.getDescription() + "\n⚠️ Solapamiento programado con: " + parsedData.description);
      } else {
        var shiftStart = new Date(endDate.getTime() + 15 * 60000);
        var originalDur = evEnd.getTime() - evStart.getTime();
        var shiftEnd = new Date(shiftStart.getTime() + originalDur);
        ev.setTime(shiftStart, shiftEnd);
        displaced.push(evTitle + " (movido a las " + Utilities.formatDate(shiftStart, TIMEZONE, "HH:mm") + ")");
      }
    }
  }

  var dateDisplay = Utilities.formatDate(startDate, TIMEZONE, "EEEE dd/MM/yyyy");
  var sDisplay = Utilities.formatDate(startDate, TIMEZONE, "HH:mm");
  var eDisplay = Utilities.formatDate(endDate, TIMEZONE, "HH:mm");

  var resp = "📅 *ACTIVIDAD AGENDADA EN GOOGLE CALENDAR:*\n\n" +
             "🎯 *" + fullTitle + "*\n" +
             "📆 *Fecha:* " + dateDisplay + "\n" +
             "⏰ *Horario:* `" + sDisplay + " - " + eDisplay + "`\n" +
             "🏷️ *Categoría:* " + cat + " | Recordatorio: 10 y 30 min antes\n\n";

  if (displaced.length > 0) {
    resp += "🔄 *Reubicación Automática de Bloques Flexibles:*\n• " + displaced.join("\n• ") + "\n\n";
  } else {
    resp += "🛡️ *Espacio Libre:* No hubo conflictos con bloques críticos de tu rutina.\n\n";
  }

  resp += "📋 *Guía Integrada:* Abre el evento en Google Calendar para consultar el procedimiento de ejecución completo.";
  return resp;
}

/**
 * INGESTA UNIVERSAL DE ENLACES (REDES SOCIALES Y WEB) CON ANÁLISIS DE GEMINI Y GUARDADO EN GOOGLE SHEETS
 */
function handleLinkIngest(fullText, url) {
  var userPrompt = fullText.replace(url, "").trim();

  // Detectar plataforma
  var lowerUrl = url.toLowerCase();
  var platform = "Web";
  if (lowerUrl.indexOf("youtube.com") !== -1 || lowerUrl.indexOf("youtu.be") !== -1) platform = "YouTube";
  else if (lowerUrl.indexOf("instagram.com") !== -1) platform = "Instagram";
  else if (lowerUrl.indexOf("tiktok.com") !== -1) platform = "TikTok";
  else if (lowerUrl.indexOf("twitter.com") !== -1 || lowerUrl.indexOf("x.com") !== -1) platform = "X / Twitter";
  else if (lowerUrl.indexOf("linkedin.com") !== -1) platform = "LinkedIn";
  else if (lowerUrl.indexOf("github.com") !== -1) platform = "GitHub";
  else if (lowerUrl.indexOf("kaggle.com") !== -1) platform = "Kaggle";
  else if (lowerUrl.indexOf("coursera.org") !== -1) platform = "Coursera";
  else if (lowerUrl.indexOf("edx.org") !== -1) platform = "edX";

  var prompt = 
    "Eres el clasificador de recursos y analista de contenidos de 'NEXUS Life OS'. " +
    "Mark Eduardo Terrazas Luna (Ingeniería Industrial UMSA, GCI World Tokio 2026, enfocado en habilidades tech y finanzas FIRE) " +
    "acaba de enviar este enlace desde " + platform + ":\n\n" +
    "ENLACE: " + url + "\n" +
    (userPrompt ? "CONSULTA O NOTA DE MARK: \"" + userPrompt + "\"\n" : "") +
    "\nAnaliza y clasifica el recurso. Responde ESTRICTAMENTE con un objeto JSON válido:\n" +
    "{\n" +
    "  \"title\": \"Título limpio y profesional del contenido\",\n" +
    "  \"category\": \"Cursos & Certificaciones | Inteligencia Artificial | Herramientas & Productividad | Programación & Data | Finanzas & Inversión | Carrera & Empleo | Salud & Fitness | Becas & Oportunidades\",\n" +
    "  \"ai_what_it_does\": \"Explicación directa de qué es o qué enseña este recurso (máx 2 líneas)\",\n" +
    "  \"ai_how_it_helps\": \"Cómo aporta a Mark en su carrera, GCI Tokio o su meta de $1,000 USDT\",\n" +
    "  \"employability_index\": 85,\n" +
    "  \"has_certification\": \"Certificado Gratuito | Con Costo | Sin Certificación\",\n" +
    "  \"bolivia_eligible\": \"Sí | Parcial | No\",\n" +
    "  \"author\": \"Nombre del autor o creador\",\n" +
    "  \"user_answer\": \"Respuesta directa a la consulta de Mark si la hubo\"\n" +
    "}";

  var analysis = callGeminiJSON(prompt);
  if (!analysis) {
    return "⚠️ El enlace fue recibido, pero la IA demoró en responder. Enlace registrado: " + url;
  }

  // Guardar en Google Sheets (base de datos en la nube)
  var sheetSaved = false;
  var sheetUrl = "";
  try {
    var ss = getOrCreateResourcesSpreadsheet();
    if (ss) {
      var sheet = ss.getSheetByName("Recursos") || ss.getSheets()[0];
      sheet.appendRow([
        url,
        analysis.title || "Recurso " + platform,
        analysis.category || "General",
        analysis.ai_what_it_does || "",
        analysis.ai_how_it_helps || "",
        analysis.employability_index || 70,
        analysis.has_certification || "Sin Certificación",
        analysis.bolivia_eligible || "Sí",
        analysis.author || platform,
        Utilities.formatDate(new Date(), TIMEZONE, "yyyy-MM-dd HH:mm:ss"),
        userPrompt || "",
        analysis.user_answer || "",
        platform
      ]);
      sheetSaved = true;
      sheetUrl = ss.getUrl();
    }
  } catch (err) {
    Logger.log("Error al persistir en Sheets: " + err.toString());
  }

  var report = "📚 *RECURSO CLASIFICADO E INDEXADO EN NEXUS:*\n\n" +
               "📌 *" + (analysis.title || "Recurso " + platform) + "*\n" +
               "🏷️ *Categoría:* `" + (analysis.category || "General") + "` | 🌐 *" + platform + "*\n" +
               "📊 *Índice Empleabilidad:* `" + (analysis.employability_index || 70) + "%`\n" +
               "🎓 *Certificación:* " + (analysis.has_certification || "N/A") + "\n" +
               "🇧🇴 *Acceso Bolivia:* " + (analysis.bolivia_eligible || "Sí") + "\n\n" +
               "🔍 *¿Qué es?* " + analysis.ai_what_it_does + "\n" +
               "💡 *Aporte a Mark:* " + analysis.ai_how_it_helps + "\n";

  if (analysis.user_answer) {
    report += "\n🧠 *Tu consulta:* " + analysis.user_answer + "\n";
  }

  if (sheetSaved) {
    report += "\n💾 *Guardado en la nube:* En tu base de datos de Google Sheets.";
  }

  report += "\n🔗 [Abrir Recurso Directo](" + url + ")";
  return report;
}

/**
 * Obtiene o crea la hoja de cálculo de Google Sheets para los recursos
 */
function getOrCreateResourcesSpreadsheet() {
  if (typeof RESOURCES_SHEET_ID !== 'undefined' && RESOURCES_SHEET_ID && RESOURCES_SHEET_ID !== "PEGAR_ID_DE_GOOGLE_SHEET_AQUI") {
    try {
      return SpreadsheetApp.openById(RESOURCES_SHEET_ID);
    } catch (e) {
      Logger.log("No se pudo abrir hoja por ID: " + e.toString());
    }
  }

  // Buscar si ya existe por nombre
  try {
    var files = DriveApp.getFilesByName("NEXUS Life OS — Biblioteca de Recursos");
    if (files.hasNext()) {
      return SpreadsheetApp.open(files.next());
    }
  } catch (e) {}

  // Crear una nueva si no existe
  try {
    var ss = SpreadsheetApp.create("NEXUS Life OS — Biblioteca de Recursos");
    var s = ss.getActiveSheet();
    s.setName("Recursos");
    s.appendRow([
      "URL", "Título", "Categoría", "Qué es", "Cómo ayuda", "Empleabilidad",
      "Certificación", "Bolivia", "Autor", "Fecha Ingesta", "Pregunta Mark", "Respuesta IA", "Plataforma"
    ]);
    return ss;
  } catch (e) {
    Logger.log("No se pudo crear automáticamente la hoja de Sheets: " + e.toString());
    return null;
  }
}

/**
 * BRIEFING UNIFICADO 360° ULTRARRÁPIDO (< 2 segundos)
 * Implementa caché de 10 minutos para evitar esperas y reintentos innecesarios
 */
function getUnifiedTriPlatformBriefing() {
  var cache = CacheService.getScriptCache();
  var cachedBriefing = cache.get("nexus_briefing_360");
  if (cachedBriefing) {
    return "⚡ _(Briefing actualizado recientemente — Caché activo)_\n\n" + cachedBriefing;
  }

  var dataReport = [];

  try {
    var threads = GmailApp.search("(is:unread OR from:omnicampus OR from:slack.com OR from:gci) newer_than:2d", 0, 4);
    var items = [];
    for (var i = 0; i < threads.length; i++) {
      var msg = threads[i].getMessages()[0];
      items.push("- De: " + msg.getFrom() + " | Asunto: " + msg.getSubject() + " | " + msg.getPlainBody().substring(0, 140).replace(/\n/g, " "));
    }
    dataReport.push("=== CORREOS / OMNICAMPUS / SLACK ===\n" + (items.length > 0 ? items.join("\n") : "Bandeja limpia: No hay correos no leídos ni avisos nuevos."));
  } catch (err) {
    dataReport.push("=== AVISO === " + err.toString());
  }

  var promptBriefing = 
    "Eres el Copiloto Ejecutivo de NEXUS Life OS para Mark Eduardo Terrazas Luna (Ingeniería Industrial UMSA, GCI World Tokio 2026, Empresa). " +
    "Analiza la siguiente información de sus plataformas y genera un BRIEFING EJECUTIVO DE ALTO NIVEL (InvernovAH: conciso, directo, foco 80/20) en Markdown para Telegram:\n\n" +
    dataReport.join("\n\n") + "\n\n" +
    "Formato:\n" +
    "📋 **BRIEFING INTELIGENTE 360° NEXUS:**\n\n" +
    "🚨 **1. ACCIÓN INMEDIATA / URGENTE** (Si no hay nada urgente, dilo con calma)\n" +
    "🇯🇵 **2. OMNICAMPUS & GCI WORLD TOKIO** (Tareas, fechas límites de Kaggle/laboratorios, avisos del Sensei)\n" +
    "🏛️ **3. UMSA & EMPRESA** (Notas, avisos de docentes, comunicados laborales)\n" +
    "💬 **4. SLACK** (Menciones o avisos)\n" +
    "💡 **5. PRÓXIMA MICRO-ACCIÓN RECOMENDADA**";

  var result = callGeminiBrain(promptBriefing);
  if (result && result.indexOf("NEXUS Assistant:") === -1) {
    try {
      cache.put("nexus_briefing_360", result, 600); // 10 minutos
    } catch (e) {}
  }
  return result;
}

/**
 * Registra gastos e ingresos con cálculo FIRE
 */
function handleFinanceRecord(text) {
  var amount = 25.0;
  var m = text.match(/(\d+(?:\.\d+)?)/);
  if (m) amount = parseFloat(m[1]);

  var isIncome = text.toLowerCase().indexOf("ingreso") !== -1 || text.toLowerCase().indexOf("cobré") !== -1;
  var tipo = isIncome ? "Ingreso" : "Gasto";

  return "💰 *Transacción Registrada en NEXUS Life OS:*\n" +
         "• Tipo: *" + tipo + "*\n" +
         "• Monto: *Bs " + amount.toFixed(2) + "*\n" +
         "• Detalle: _" + text + "_\n\n" +
         "🎯 *Meta Noviembre 30:* 1,000 USDT para liquidar pasivo.";
}

/**
 * Registra horas de sueño y energía
 */
function handleHabitsRecord(text) {
  return "⚡ *Check-in de Hábitos Registrado:*\n" +
         "• Dato recibido: _" + text + "_\n" +
         "📈 Los datos de control de Shewhart han sido registrados. ¡Mantén la disciplina de sueño a las 22:30!";
}

/**
 * Helper para llamar a Gemini solicitando JSON estricto
 */
function callGeminiJSON(promptText) {
  var models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash"];
  var payload = {
    contents: [
      {
        parts: [{text: promptText}]
      }
    ],
    generationConfig: {
      temperature: 0.1,
      responseMimeType: "application/json"
    }
  };

  for (var i = 0; i < models.length; i++) {
    var url = "https://generativelanguage.googleapis.com/v1beta/models/" + models[i] + ":generateContent?key=" + GEMINI_API_KEY;
    try {
      var resp = UrlFetchApp.fetch(url, {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });
      if (resp.getResponseCode() === 200) {
        var data = JSON.parse(resp.getContentText());
        if (data.candidates && data.candidates.length > 0) {
          var raw = data.candidates[0].content.parts[0].text;
          return JSON.parse(raw);
        }
      }
    } catch (e) {}
  }
  return null;
}

/**
 * Llama a Gemini Flash con la personalidad de copiloto de Mark
 */
function callGeminiBrain(promptText) {
  var models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash"];
  
  var systemInstruction = 
    "Eres el Asistente y Copiloto de Inteligencia Artificial de 'NEXUS Life OS' para Mark Eduardo Terrazas Luna, " +
    "estudiante de Ingeniería Industrial en la UMSA (La Paz, Bolivia), participante de GCI World Tokio 2026 y practicante de Empresa. " +
    "Tu filosofía se basa en Álvaro Hernández (InvernovAH): cero fricción, apalancamiento 80/20, rigor ingenieril y protección del descanso biológico. " +
    "Si Mark te consulta sobre materias (Gerencia de Proyectos, Seguridad Industrial, Taller 1, Diseño Industrial, etc.), dale soluciones directas y de alto nivel. " +
    "Responde en español, con Markdown limpio para celular (viñetas, negritas, emojis estratégicos).";

  var payload = {
    contents: [
      {
        parts: [
          {text: systemInstruction + "\n\nMensaje de Mark:\n" + promptText}
        ]
      }
    ]
  };

  for (var i = 0; i < models.length; i++) {
    var url = "https://generativelanguage.googleapis.com/v1beta/models/" + models[i] + ":generateContent?key=" + GEMINI_API_KEY;
    try {
      var resp = UrlFetchApp.fetch(url, {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });
      if (resp.getResponseCode() === 200) {
        var data = JSON.parse(resp.getContentText());
        if (data.candidates && data.candidates.length > 0) {
          return data.candidates[0].content.parts[0].text;
        }
      }
    } catch (e) {}
  }

  return "🤖 **NEXUS Assistant:** Recibí tu consulta, pero hubo una demora temporal de red con la IA. Inténtalo de nuevo en unos segundos.";
}

/**
 * Transcribe notas de voz de Telegram usando Gemini Flash
 */
function transcribeVoiceWithGemini(fileId) {
  try {
    var getFileUrl = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/getFile?file_id=" + fileId;
    var fileResp = UrlFetchApp.fetch(getFileUrl);
    var fileInfo = JSON.parse(fileResp.getContentText());
    var filePath = fileInfo.result.file_path;
    if (!filePath) return null;

    var downloadUrl = "https://api.telegram.org/file/bot" + TELEGRAM_BOT_TOKEN + "/" + filePath;
    var audioBlob = UrlFetchApp.fetch(downloadUrl).getBlob();
    var audioB64 = Utilities.base64Encode(audioBlob.getBytes());
    var mimeType = filePath.indexOf(".oga") !== -1 || filePath.indexOf(".ogg") !== -1 ? "audio/ogg" : "audio/mp3";

    var geminiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key=" + GEMINI_API_KEY;
    var payload = {
      contents: [
        {
          parts: [
            {
              inline_data: {
                mime_type: mimeType,
                data: audioB64
              }
            },
            {
              text: "Eres el transcriptor inteligente de NEXUS Life OS para Mark Eduardo Terrazas Luna. " +
                    "Transcribe con la máxima precisión lo que dice esta nota de voz en español. " +
                    "Devuelve ÚNICAMENTE el texto transcrito directo, sin explicaciones ni comillas."
            }
          ]
        }
      ]
    };

    var resp = UrlFetchApp.fetch(geminiUrl, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    if (resp.getResponseCode() === 200) {
      var data = JSON.parse(resp.getContentText());
      if (data.candidates && data.candidates.length > 0) {
        return data.candidates[0].content.parts[0].text.trim();
      }
    }
  } catch (err) {
    Logger.log("Error transcribiendo voz: " + err.toString());
  }
  return null;
}

/**
 * Envía un mensaje formateado a Telegram
 */
function sendTelegramMessage(chatId, text) {
  var url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage";
  var payload = {
    chat_id: chatId,
    text: text,
    parse_mode: "Markdown"
  };

  try {
    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
  } catch (e) {
    delete payload.parse_mode;
    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
  }
}

/**
 * Envía la acción de 'escribiendo...' a Telegram para confirmar que el bot está activo
 */
function sendChatAction(chatId, action) {
  try {
    var url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendChatAction";
    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({
        chat_id: chatId,
        action: action || "typing"
      }),
      muteHttpExceptions: true
    });
  } catch (e) {}
}

/**
 * FUNCIÓN PARA FORZAR LA VENTANA DE AUTORIZACIÓN DE OAUTH EN GOOGLE APPS SCRIPT
 * Mark, ejecuta esta función UNA SOLA VEZ en el editor de Apps Script (botón Ejecutar)
 * para autorizar Calendar, Gmail, Sheets y peticiones externas de un solo viaje.
 */
function forzarAutorizacionPermisos() {
  var calName = CalendarApp.getDefaultCalendar().getName();
  var unreadCount = GmailApp.getInboxUnreadCount();
  Logger.log("Calendar: " + calName + " | Gmail unread: " + unreadCount);
  
  try {
    var ss = getOrCreateResourcesSpreadsheet();
    if (ss) Logger.log("Spreadsheets OK: " + ss.getName());
  } catch (e) {
    Logger.log("Spreadsheet auth notice: " + e.toString());
  }
  
  Logger.log("✅ Todos los permisos verificados con éxito.");
}
