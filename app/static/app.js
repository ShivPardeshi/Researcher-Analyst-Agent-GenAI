/**
 * Research Analyst Agents Frontend Client Logic
 * Coordinates 3-Agent visual pipeline, request submission, media/PDF/Web RAG & report formatting.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Main Form Elements
  const form = document.getElementById("legalForm");
  const questionInput = document.getElementById("questionInput");
  const charCount = document.getElementById("charCount");
  const submitBtn = document.getElementById("submitBtn");
  const clearBtn = document.getElementById("clearBtn");
  const copyBtn = document.getElementById("copyBtn");
  const printBtn = document.getElementById("printBtn");
  const memoTimestamp = document.getElementById("memoTimestamp");

  // System Status Elements
  const systemStatus = document.getElementById("systemStatus");
  const statusLabel = document.getElementById("statusLabel");
  const modelTag = document.getElementById("modelTag");

  // View Container Elements
  const emptyView = document.getElementById("emptyView");
  const loadingView = document.getElementById("loadingView");
  const loadingLabel = document.getElementById("loadingLabel");
  const loadingCaption = document.getElementById("loadingCaption");
  const errorView = document.getElementById("errorView");
  const errorMsg = document.getElementById("errorMsg");
  const responseView = document.getElementById("responseView");

  // Report Elements
  const sourcesBlock = document.getElementById("sourcesBlock");
  const sourcesTags = document.getElementById("sourcesTags");
  const answerArticle = document.getElementById("answerArticle");
  const disclaimerNotice = document.getElementById("disclaimerNotice");

  // Evidence Media Elements
  const evidenceMediaPanel = document.getElementById("evidenceMediaPanel");
  const evidenceMediaGrid = document.getElementById("evidenceMediaGrid");
  const mediaCountBadge = document.getElementById("mediaCountBadge");

  // Pipeline Step Elements
  const pipe1 = document.getElementById("pipe1");
  const pipe2 = document.getElementById("pipe2");
  const pipe3 = document.getElementById("pipe3");

  // Media Attachment Controls
  const tabUpload = document.getElementById("tabUpload");
  const tabUrl = document.getElementById("tabUrl");
  const tabPresets = document.getElementById("tabPresets");
  const panelUpload = document.getElementById("panelUpload");
  const panelUrl = document.getElementById("panelUrl");
  const panelPresets = document.getElementById("panelPresets");

  const imageDropzone = document.getElementById("imageDropzone");
  const imageFileInput = document.getElementById("imageFileInput");
  const imageUrlInput = document.getElementById("imageUrlInput");
  const loadUrlBtn = document.getElementById("loadUrlBtn");

  const attachedMediaCard = document.getElementById("attachedMediaCard");
  const attachedThumbnail = document.getElementById("attachedThumbnail");
  const attachedPdfIcon = document.getElementById("attachedPdfIcon");
  const attachedFilename = document.getElementById("attachedFilename");
  const attachedSize = document.getElementById("attachedSize");
  const attachedTypeBadge = document.getElementById("attachedTypeBadge");
  const previewZoomBtn = document.getElementById("previewZoomBtn");
  const removeMediaBtn = document.getElementById("removeMediaBtn");

  // Modern Centered Modal Lightbox Overlay
  const mediaLightbox = document.getElementById("mediaLightbox");
  const lightboxCard = document.getElementById("lightboxCard");
  const lightboxImg = document.getElementById("lightboxImg");
  const lightboxTitle = document.getElementById("lightboxTitle");
  const lightboxCaption = document.getElementById("lightboxCaption");
  const lightboxZoomBtn = document.getElementById("lightboxZoomBtn");
  const lightboxDownloadBtn = document.getElementById("lightboxDownloadBtn");
  const lightboxCloseBtn = document.getElementById("lightboxCloseBtn");

  // Internal State
  let latestReportRaw = "";
  let pipelineTimer = null;
  let currentAttachment = {
    type: null, // "image" | "pdf" | "web"
    base64: null,
    filename: null,
    mime: null,
    url: null,
  };

  // Initialize Backend Status
  verifyBackendStatus();

  // Character counter
  questionInput.addEventListener("input", () => {
    charCount.textContent = questionInput.value.length;
  });

  // Curated Research Topic Chips
  document.querySelectorAll(".suggestion-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      questionInput.value = btn.getAttribute("data-query");
      charCount.textContent = questionInput.value.length;
      questionInput.focus();
    });
  });

  // Media Tabs Navigation
  const mediaTabs = [
    { btn: tabUpload, panel: panelUpload },
    { btn: tabUrl, panel: panelUrl },
    { btn: tabPresets, panel: panelPresets },
  ];

  mediaTabs.forEach(({ btn, panel }) => {
    if (!btn || !panel) return;
    btn.addEventListener("click", () => {
      mediaTabs.forEach((t) => {
        if (t.btn) t.btn.classList.remove("active");
        if (t.panel) t.panel.style.display = "none";
      });
      btn.classList.add("active");
      panel.style.display = "block";
    });
  });

  // Dropzone Interaction
  if (imageDropzone && imageFileInput) {
    imageDropzone.addEventListener("click", () => {
      imageFileInput.click();
    });

    imageFileInput.addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        processUploadedFile(file);
      }
    });

    // Drag and Drop Events
    ["dragenter", "dragover"].forEach((eventName) => {
      imageDropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        imageDropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      imageDropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        imageDropzone.classList.remove("dragover");
      });
    });

    imageDropzone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const file = dt && dt.files && dt.files[0];
      if (file) {
        processUploadedFile(file);
      }
    });
  }

  // Global Clipboard Paste Support (Cmd+V / Ctrl+V)
  window.addEventListener("paste", (e) => {
    const items = (e.clipboardData || e.originalEvent?.clipboardData)?.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          processUploadedFile(file, "Pasted_Screenshot_" + Date.now() + ".png");
          break;
        }
      }
    }
  });

  // URL Input Loader (Web Scraping RAG)
  if (loadUrlBtn && imageUrlInput) {
    loadUrlBtn.addEventListener("click", () => {
      const url = imageUrlInput.value.trim();
      if (!url) return;
      attachWebScrapeUrl(url);
    });

    imageUrlInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        loadUrlBtn.click();
      }
    });
  }

  // Sample Preset Benchmark Chart Chips
  document.querySelectorAll(".preset-chart-chip").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const imgUrl = btn.getAttribute("data-img");
      const imgName = btn.getAttribute("data-name");
      const query = btn.getAttribute("data-query");

      if (query && (!questionInput.value || questionInput.value.trim().length < 5)) {
        questionInput.value = query;
        charCount.textContent = questionInput.value.length;
      }

      try {
        const res = await fetch(imgUrl);
        const textSvg = await res.text();
        const base64Data = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(textSvg)));

        setAttachmentState({
          type: "image",
          base64: base64Data,
          filename: imgName,
          mime: "image/svg+xml",
          url: imgUrl,
          size: "5.1 KB",
          badge: "BENCHMARK",
        });
      } catch (err) {
        setAttachmentState({
          type: "image",
          base64: null,
          filename: imgName,
          mime: "image/svg+xml",
          url: imgUrl,
          size: "Preset Vector",
          badge: "PRESET",
        });
      }
    });
  });

  // Remove Attached Media / Document
  if (removeMediaBtn) {
    removeMediaBtn.addEventListener("click", () => {
      clearAttachment();
    });
  }

  // Zoom Button on Attached Preview
  if (previewZoomBtn) {
    previewZoomBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const src = currentAttachment.url || currentAttachment.base64 || attachedThumbnail.src;
      if (src && currentAttachment.type === "image") {
        openLightbox(
          src,
          currentAttachment.filename || "Attached Research Artifact",
          "User-attached empirical evidence artifact."
        );
      }
    });
  }

  // Click on thumbnail directly also opens Lightbox
  if (attachedThumbnail) {
    attachedThumbnail.addEventListener("click", () => {
      if (previewZoomBtn) previewZoomBtn.click();
    });
  }

  // Clear All Form Fields & Attachments
  clearBtn.addEventListener("click", () => {
    questionInput.value = "";
    charCount.textContent = "0";
    clearAttachment();
    showView("empty");
    resetPipeline();
    questionInput.focus();
  });

  // Copy Report Text
  copyBtn.addEventListener("click", async () => {
    if (!latestReportRaw) return;
    try {
      await navigator.clipboard.writeText(latestReportRaw);
      const span = copyBtn.querySelector("span");
      const originalText = span.textContent;
      span.textContent = "Copied!";
      setTimeout(() => {
        span.textContent = originalText;
      }, 2000);
    } catch (e) {
      console.warn("Failed to copy report text: ", e);
    }
  });

  // Print Report Button
  if (printBtn) {
    printBtn.addEventListener("click", () => {
      window.print();
    });
  }

  // Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = questionInput.value.trim();
    const hasAttachment = Boolean(
      currentAttachment.base64 || currentAttachment.url || currentAttachment.type
    );

    if (!query && !hasAttachment) return;
    if (query && query.length < 4 && !hasAttachment) return;

    // UI state: loading
    showView("loading");
    setSubmitState(true);
    startPipelineAnimation();

    const payload = {
      topic: query || undefined,
    };

    if (currentAttachment.type === "image") {
      payload.image_base64 = currentAttachment.base64 || undefined;
      payload.image_filename = currentAttachment.filename || undefined;
      payload.image_mime_type = currentAttachment.mime || undefined;
      payload.image_url = currentAttachment.url || undefined;
    } else if (currentAttachment.type === "pdf") {
      payload.pdf_base64 = currentAttachment.base64 || undefined;
      payload.pdf_filename = currentAttachment.filename || undefined;
    } else if (currentAttachment.type === "web") {
      payload.web_urls = currentAttachment.url ? [currentAttachment.url] : undefined;
    }

    try {
      const response = await fetch("/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Server error (${response.status})`);
      }

      finishPipelineAnimation();
      latestReportRaw = data.report || data.answer || "No report generated.";

      renderReport(latestReportRaw);
      renderMedia(data.media || []);
      renderSources(data.sources || []);
      renderDisclaimer(data.disclaimer);

      if (memoTimestamp) {
        memoTimestamp.textContent = new Date().toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        });
      }

      showView("response");
    } catch (err) {
      stopPipelineAnimation();
      errorMsg.textContent = err.message || "Failed to complete research analysis.";
      showView("error");
    } finally {
      setSubmitState(false);
    }
  });

  // Process File Uploaded via Dropzone or Picker (Handles PDF & Images)
  function processUploadedFile(file, customName = null) {
    const filename = customName || file.name || "research_document";
    const sizeFormatted = formatFileSize(file.size);
    const isPdf = filename.toLowerCase().endsWith(".pdf") || file.type === "application/pdf";

    const reader = new FileReader();
    reader.onload = (e) => {
      if (isPdf) {
        setAttachmentState({
          type: "pdf",
          base64: e.target.result,
          filename: filename,
          mime: "application/pdf",
          url: null,
          size: sizeFormatted,
          badge: "PDF (RAG)",
        });
      } else {
        setAttachmentState({
          type: "image",
          base64: e.target.result,
          filename: filename,
          mime: file.type || "image/png",
          url: null,
          size: sizeFormatted,
          badge: getExtension(filename).toUpperCase() || "IMAGE",
        });
      }
    };
    reader.readAsDataURL(file);
  }

  // Attach Web Scrape URL
  function attachWebScrapeUrl(url) {
    let cleanUrl = url.trim();
    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      cleanUrl = "https://" + cleanUrl;
    }

    setAttachmentState({
      type: "web",
      base64: null,
      filename: cleanUrl,
      mime: "text/html",
      url: cleanUrl,
      size: "Live Web Scrape",
      badge: "WEB RAG",
    });
  }

  // Update State & UI for Attached Media / Documents
  function setAttachmentState({ type, base64, filename, mime, url, size, badge }) {
    currentAttachment = { type, base64, filename, mime, url };

    attachedFilename.textContent = filename || "attachment";
    attachedSize.textContent = size || "";
    attachedTypeBadge.textContent = badge || "ATTACHED";

    if (type === "pdf") {
      attachedThumbnail.style.display = "none";
      attachedPdfIcon.style.display = "flex";
      previewZoomBtn.style.display = "none";
    } else if (type === "web") {
      attachedThumbnail.style.display = "none";
      attachedPdfIcon.style.display = "flex";
      attachedPdfIcon.innerHTML = `
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="2" y1="12" x2="22" y2="12"></line>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
        </svg>
      `;
      previewZoomBtn.style.display = "none";
    } else {
      // Image
      attachedThumbnail.src = url || base64;
      attachedThumbnail.style.display = "block";
      attachedPdfIcon.style.display = "none";
      previewZoomBtn.style.display = "flex";
    }

    attachedMediaCard.style.display = "flex";

    // Switch to upload tab
    if (tabUpload && panelUpload) {
      mediaTabs.forEach((t) => {
        if (t.btn) t.btn.classList.remove("active");
        if (t.panel) t.panel.style.display = "none";
      });
      tabUpload.classList.add("active");
      panelUpload.style.display = "block";
    }
  }

  // Clear Attachment
  function clearAttachment() {
    currentAttachment = { type: null, base64: null, filename: null, mime: null, url: null };
    attachedThumbnail.src = "";
    attachedThumbnail.style.display = "none";
    attachedPdfIcon.style.display = "none";
    attachedFilename.textContent = "";
    attachedSize.textContent = "";
    attachedMediaCard.style.display = "none";
    if (imageFileInput) imageFileInput.value = "";
    if (imageUrlInput) imageUrlInput.value = "";
  }

  // Format File Size
  function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return "0 KB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  }

  function getExtension(name) {
    if (!name || name.indexOf(".") === -1) return "FILE";
    return name.split(".").pop();
  }

  // Render Visual Evidence & Grounding Media Panel
  function renderMedia(mediaList) {
    if (!evidenceMediaPanel || !evidenceMediaGrid) return;

    if (!mediaList || mediaList.length === 0) {
      evidenceMediaPanel.style.display = "none";
      return;
    }

    evidenceMediaGrid.innerHTML = "";
    mediaCountBadge.textContent = `${mediaList.length} ${mediaList.length === 1 ? "Item" : "Items"}`;

    mediaList.forEach((item) => {
      const card = document.createElement("div");
      card.className = "evidence-media-card";

      const title = item.title || "Visual Evidence";
      const caption = item.caption || "Empirical evidence diagram";
      const src = item.url || "";
      const isPdf = item.type === "pdf";

      if (isPdf) {
        card.innerHTML = `
          <div class="evidence-media-thumb-frame" style="background: #1e293b; display: flex; align-items: center; justify-content: center;">
            <div style="color: #ef4444; text-align: center;">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
              </svg>
              <div style="font-size: 0.72rem; font-weight: 700; color: #f87171; margin-top: 4px;">PDF RAG DOCUMENT</div>
            </div>
          </div>
          <div class="evidence-media-info">
            <div class="evidence-media-title">${title}</div>
            <div class="evidence-media-caption">${caption}</div>
          </div>
        `;
      } else {
        card.innerHTML = `
          <div class="evidence-media-thumb-frame">
            <img src="${src}" alt="${title}" class="evidence-media-thumb" loading="lazy">
            <div class="evidence-media-overlay">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                <line x1="11" y1="8" x2="11" y2="14"></line>
                <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg>
              <span>Click to Inspect</span>
            </div>
          </div>
          <div class="evidence-media-info">
            <div class="evidence-media-title">${title}</div>
            <div class="evidence-media-caption">${caption}</div>
          </div>
        `;

        card.addEventListener("click", () => {
          openLightbox(src, title, caption);
        });
      }

      evidenceMediaGrid.appendChild(card);
    });

    evidenceMediaPanel.style.display = "block";
  }

  // Lightbox Controller (Centered Modal Overlay)
  function openLightbox(src, title, caption) {
    if (!mediaLightbox) return;
    lightboxImg.src = src;
    lightboxImg.classList.remove("zoomed");
    lightboxTitle.textContent = title || "Research Evidence";
    lightboxCaption.textContent = caption || "";
    if (lightboxDownloadBtn) {
      lightboxDownloadBtn.href = src;
    }
    mediaLightbox.style.display = "flex";
    setTimeout(() => {
      mediaLightbox.classList.add("active");
    }, 10);
  }

  function closeLightbox() {
    if (!mediaLightbox) return;
    mediaLightbox.classList.remove("active");
    setTimeout(() => {
      mediaLightbox.style.display = "none";
      lightboxImg.classList.remove("zoomed");
    }, 200);
  }

  if (lightboxCloseBtn) {
    lightboxCloseBtn.addEventListener("click", closeLightbox);
  }

  if (lightboxZoomBtn) {
    lightboxZoomBtn.addEventListener("click", () => {
      lightboxImg.classList.toggle("zoomed");
    });
  }

  if (lightboxImg) {
    lightboxImg.addEventListener("click", () => {
      lightboxImg.classList.toggle("zoomed");
    });
  }

  // Light-dismiss: click on overlay backdrop closes lightbox
  if (mediaLightbox) {
    mediaLightbox.addEventListener("click", (e) => {
      if (e.target === mediaLightbox) {
        closeLightbox();
      }
    });
  }

  // Escape key closes lightbox
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && mediaLightbox && mediaLightbox.classList.contains("active")) {
      closeLightbox();
    }
  });

  // Backend Healthcheck
  async function verifyBackendStatus() {
    try {
      const res = await fetch("/health");
      if (!res.ok) throw new Error("Health check failed");
      const health = await res.json();

      systemStatus.classList.remove("error");
      systemStatus.classList.add("healthy");
      statusLabel.textContent = "Multi-Agent System Ready";
      if (modelTag && health.model) {
        modelTag.textContent = health.model;
      }
    } catch (err) {
      systemStatus.classList.remove("healthy");
      systemStatus.classList.add("error");
      statusLabel.textContent = "Service Offline";
    }
  }

  // Pipeline Animation
  function resetPipeline() {
    [pipe1, pipe2, pipe3].forEach((el) => {
      if (el) el.classList.remove("active", "completed");
    });
  }

  function startPipelineAnimation() {
    resetPipeline();
    if (pipe1) pipe1.classList.add("active");
    loadingLabel.textContent = "Agent 1: Research Agent Gathering Information...";
    loadingCaption.textContent = "Searching research knowledge base, parsing PDF/web RAG, and compiling evidence...";

    let step = 1;
    pipelineTimer = setInterval(() => {
      step++;
      if (step === 2) {
        if (pipe1) {
          pipe1.classList.remove("active");
          pipe1.classList.add("completed");
        }
        if (pipe2) pipe2.classList.add("active");
        loadingLabel.textContent = "Agent 2: Analysis & Verification Agent Auditing...";
        loadingCaption.textContent = "Validating empirical claims, detecting uncertainties, and cross-examining citations...";
      } else if (step === 3) {
        if (pipe2) {
          pipe2.classList.remove("active");
          pipe2.classList.add("completed");
        }
        if (pipe3) pipe3.classList.add("active");
        loadingLabel.textContent = "Agent 3: Report Generation Agent Synthesizing...";
        loadingCaption.textContent = "Formatting publication-grade executive sections, RAG findings, and diagrams...";
      }
    }, 4500);
  }

  function finishPipelineAnimation() {
    clearInterval(pipelineTimer);
    [pipe1, pipe2, pipe3].forEach((el) => {
      if (el) {
        el.classList.remove("active");
        el.classList.add("completed");
      }
    });
  }

  function stopPipelineAnimation() {
    clearInterval(pipelineTimer);
    resetPipeline();
  }

  function setSubmitState(isSubmitting) {
    submitBtn.disabled = isSubmitting;
    if (isSubmitting) {
      submitBtn.classList.add("btn-loading");
    } else {
      submitBtn.classList.remove("btn-loading");
    }
  }

  function showView(view) {
    emptyView.style.display = view === "empty" ? "flex" : "none";
    loadingView.style.display = view === "loading" ? "flex" : "none";
    errorView.style.display = view === "error" ? "flex" : "none";
    responseView.style.display = view === "response" ? "block" : "none";

    copyBtn.style.display = view === "response" ? "inline-flex" : "none";
    if (printBtn) {
      printBtn.style.display = view === "response" ? "inline-flex" : "none";
    }
  }

  function renderSources(sources) {
    if (!sources || sources.length === 0) {
      sourcesBlock.style.display = "none";
      return;
    }
    sourcesTags.innerHTML = "";
    sources.forEach((src) => {
      const tag = document.createElement("span");
      tag.className = "source-tag";
      tag.textContent = src;
      sourcesTags.appendChild(tag);
    });
    sourcesBlock.style.display = "block";
  }

  function renderDisclaimer(text) {
    if (disclaimerNotice) {
      disclaimerNotice.textContent = text || "";
    }
  }

  function renderReport(markdown) {
    answerArticle.innerHTML = parseMarkdownToHTML(markdown);

    // Attach click listener to report figures to open in Lightbox
    answerArticle.querySelectorAll(".report-figure").forEach((fig) => {
      fig.addEventListener("click", () => {
        const src = fig.getAttribute("data-src");
        const caption = fig.getAttribute("data-caption") || "Research Figure";
        if (src) {
          openLightbox(src, caption, "Grounding benchmark figure embedded in research report.");
        }
      });
    });
  }

  // Enhanced Markdown parser with Image, Blockquote, Table & List support
  function parseMarkdownToHTML(md) {
    if (!md) return "";

    const lines = md.split("\n");
    let html = "";
    let inList = false;
    let inOrderedList = false;
    let inBlockquote = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      // Markdown Images: ![Alt Text](url)
      const imageMatch = line.trim().match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
      if (imageMatch) {
        closeLists();
        const alt = imageMatch[1] || "Research Diagram";
        const src = imageMatch[2];
        html += `
          <figure class="report-figure" data-src="${src}" data-caption="${alt}">
            <div class="figure-img-frame">
              <img src="${src}" alt="${alt}" loading="lazy" class="figure-img">
              <div class="figure-hover-action">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="11" y1="8" x2="11" y2="14"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
                </svg>
                <span>Inspect Full Size</span>
              </div>
            </div>
            <figcaption class="figure-caption">
              <span class="caption-icon">📊</span>
              <span>${alt}</span>
            </figcaption>
          </figure>
        `;
        continue;
      }

      // Blockquotes
      if (line.startsWith("> ")) {
        if (!inBlockquote) {
          html += "<blockquote>";
          inBlockquote = true;
        }
        line = line.substring(2);
      } else if (inBlockquote) {
        html += "</blockquote>";
        inBlockquote = false;
      }

      // Headings
      if (line.startsWith("### ")) {
        closeLists();
        html += `<h3>${formatInline(line.substring(4))}</h3>`;
        continue;
      }
      if (line.startsWith("## ")) {
        closeLists();
        html += `<h2>${formatInline(line.substring(3))}</h2>`;
        continue;
      }
      if (line.startsWith("# ")) {
        closeLists();
        html += `<h1>${formatInline(line.substring(2))}</h1>`;
        continue;
      }

      // Unordered lists
      if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        if (!inList) {
          if (inOrderedList) {
            html += "</ol>";
            inOrderedList = false;
          }
          html += "<ul>";
          inList = true;
        }
        const itemContent = line.trim().substring(2);
        html += `<li>${formatInline(itemContent)}</li>`;
        continue;
      }

      // Ordered lists (e.g. 1. )
      const orderedMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (orderedMatch) {
        if (!inOrderedList) {
          if (inList) {
            html += "</ul>";
            inList = false;
          }
          html += "<ol>";
          inOrderedList = true;
        }
        html += `<li>${formatInline(orderedMatch[2])}</li>`;
        continue;
      }

      // If we were in a list and hit a non-list item
      closeLists();

      // Empty line / paragraph separation
      if (!line.trim()) {
        continue;
      }

      // Horizontal rule
      if (line.trim() === "---" || line.trim() === "***") {
        html += "<hr>";
        continue;
      }

      // Standard paragraph
      html += `<p>${formatInline(line)}</p>`;
    }

    closeLists();
    if (inBlockquote) html += "</blockquote>";

    return html;

    function closeLists() {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      if (inOrderedList) {
        html += "</ol>";
        inOrderedList = false;
      }
    }

    function formatInline(text) {
      let formatted = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, alt, src) => {
        return `<figure class="report-figure" data-src="${src}" data-caption="${alt}">
          <div class="figure-img-frame">
            <img src="${src}" alt="${alt}" loading="lazy" class="figure-img">
          </div>
          <figcaption class="figure-caption">
            <span class="caption-icon">📊</span>
            <span>${alt}</span>
          </figcaption>
        </figure>`;
      });

      return formatted
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    }
  }
});
