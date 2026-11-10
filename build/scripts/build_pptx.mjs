import { readFile, writeFile } from "node:fs/promises";
import { extname, basename } from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const [specPath, outputPath, screenshotPath, markdownPath, documentSpecPath] = process.argv.slice(2);
if (!specPath || !outputPath) {
  throw new Error("Usage: node build_pptx.mjs spec.json output.pptx [prototype.png] [presentation.md] [document-spec.json]");
}

const spec = JSON.parse(await readFile(specPath, "utf8"));
const { theme } = spec;
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const noLine = { fill: "none", width: 0 };
const imagePosition = { left: 68, top: 126, width: 1144, height: 524 };

function text(slide, name, value, left, top, width, height, size, options = {}) {
  const shape = slide.shapes.add({
    name,
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: noLine,
  });
  shape.text = value;
  shape.text.style = {
    typeface: theme.font_name,
    fontSize: size,
    color: `#${theme.body_color}`,
    insets: 0,
    autoFit: "none",
    verticalAlignment: "middle",
    ...options,
  };
}

for (const [index, item] of spec.slides.entries()) {
  const slide = deck.slides.add();
  slide.background.fill = `#${theme.background_color}`;
  text(slide, "slide-title", item.title, 68, 50, 1144, 60, 43, {
    bold: true,
    color: `#${theme.heading_color}`,
  });
  text(slide, "slide-number", String(index + 1), 1152, 667, 60, 26, 17, {
    alignment: "right",
  });

  const roster = item.content.find(block => block.type === "table");
  const screenshot = item.content.find(block => block.type === "screenshot");
  if (roster) {
    const values = [roster.header, ...roster.rows];
    const isRoster = roster.header.length === 2;
    const rowHeight = isRoster ? 45 : 44;
    const table = slide.tables.add({
      rows: values.length,
      columns: roster.header.length,
      left: 68,
      top: 132,
      width: isRoster ? 1040 : 1144,
      height: rowHeight * values.length,
      columnWidths: isRoster ? [650, 390] : [310, 160, 160, 514],
      values,
    });
    for (const [row, cells] of values.entries()) {
      table.rows[row].height = rowHeight;
      for (const [column] of cells.entries()) {
        const cell = table.getCell(row, column);
        cell.fill = row === 0 ? "#EAEAEA" : "#FFFFFF";
        cell.text.style = {
          typeface: theme.font_name,
          fontSize: 24,
          color: `#${theme.body_color}`,
          bold: row === 0,
          verticalAlignment: "middle",
        };
      }
    }
    table.borders.assign({ fill: "#D6D6D6", width: 1, style: "solid" });
    if (!isRoster) {
      const lesson = item.content.find(block => block.type === "section");
      const reflection = item.content.find(block => block.type === "para");
      text(slide, "lesson-heading", lesson.heading, 68, 378, 1144, 35, 27, { bold: true });
      text(slide, "lesson-body", lesson.text, 68, 421, 1100, 112, 24, { verticalAlignment: "top", wrap: "square" });
      text(slide, "reflection-limit", reflection.text, 68, 548, 1100, 70, 24, { verticalAlignment: "top", wrap: "square" });
    }
  } else if (screenshot) {
    if (screenshotPath) {
      const contentType = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg" }[
        extname(screenshotPath).toLowerCase()
      ];
      if (!contentType) throw new Error("Use a PNG or JPEG for the prototype screenshot.");
      slide.images.add({
        blob: await readFile(screenshotPath),
        contentType,
        alt: "Close of Day prototype with sample data",
        fit: "contain",
        position: imagePosition,
      });
    } else {
      slide.shapes.add({
        name: "screenshot-frame",
        geometry: "rect",
        position: imagePosition,
        fill: "none",
        line: { fill: "#555555", width: 1.5, style: "dashed" },
      });
      text(slide, "screenshot-placeholder", screenshot.text, 115, 345, 1050, 46, 29, {
        bold: true,
        alignment: "center",
      });
      text(slide, "screenshot-content", "Business date, payment activity and cash variance", 115, 406, 1050, 42, 24, {
        alignment: "center",
      });
    }
    text(slide, "sample-data-caption", screenshot.caption, 68, 657, 1050, 35, 19);
  } else {
    const spacing = item.content.length === 4 ? 120 : 152;
    for (const [i, section] of item.content.entries()) {
      if (section.type === "para") {
        text(slide, `cover-detail-${i + 1}`, section.text, 68, 166 + i * 62, 1144, 46, 28);
        continue;
      }
      const y = 139 + i * spacing;
      text(slide, `section-${i + 1}-heading`, section.heading, 68, y, 1144, 35, 27, { bold: true });
      text(slide, `section-${i + 1}-body`, section.text, 68, y + 43, 1100, 70, theme.font_size * 4 / 3, {
        verticalAlignment: "top",
        wrap: "square",
      });
    }
  }

  slide.speakerNotes.text = (item.notes || []).join("\n\n");
}
await (await PresentationFile.exportPptx(deck)).save(outputPath);


// Derive the reading version and legacy document spec from the same slide data.
// Optional outputs avoid maintaining contradictory presentation outlines by hand.
const imageName = screenshotPath ? basename(screenshotPath) : "PhaseFinal_Close-of-Day.png";
const markdown = ["# Deniz Construction Management System", "", "Group K | SWE2102 Requirements Engineering | 10 November 2026", ""];
const documentSpec = { title: spec.title, meta: ["Course: SWE2102 Requirements Engineering", "Group: K", "Presentation date: 10 November 2026"], blocks: [] };
for (const [index, slide] of spec.slides.entries()) {
  markdown.push(`## ${index + 1}. ${slide.title}`, "");
  documentSpec.blocks.push({ type: "h1", text: `Slide ${index + 1}: ${slide.title}` });
  for (const block of slide.content) {
    if (block.type === "table") {
      markdown.push(`| ${block.header.join(" | ")} |`, `|${block.header.map(() => "---").join("|")}|`, ...block.rows.map(row => `| ${row.join(" | ")} |`), "");
      documentSpec.blocks.push(block);
    } else if (block.type === "section") {
      markdown.push(`**${block.heading}**`, "", block.text, "");
      documentSpec.blocks.push({ type: "para", runs: [{ text: block.heading + ". ", bold: true }, { text: block.text }] });
    } else if (block.type === "screenshot") {
      markdown.push(`![Saved Close of Day report](${imageName})`, "", block.caption, "");
      documentSpec.blocks.push({ type: "para", text: `Screenshot: ${imageName}. ${block.caption}` });
    } else {
      markdown.push(block.text, "");
      documentSpec.blocks.push(block);
    }
  }
  markdown.push("**Speaker notes**", "", ...(slide.notes || []).flatMap(note => [note, ""]));
  documentSpec.blocks.push({ type: "h2", text: "Speaker notes" }, ...(slide.notes || []).map(text => ({ type: "para", text })));
  if (index < spec.slides.length - 1) documentSpec.blocks.push({ type: "pagebreak" });
}
if (markdownPath) await writeFile(markdownPath, markdown.join("\n"));
if (documentSpecPath) await writeFile(documentSpecPath, JSON.stringify(documentSpec, null, 2) + "\n");
