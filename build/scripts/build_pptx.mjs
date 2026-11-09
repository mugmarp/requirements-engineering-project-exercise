import { readFile } from "node:fs/promises";
import { extname } from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const [specPath, outputPath, screenshotPath] = process.argv.slice(2);
if (!specPath || !outputPath) {
  throw new Error("Usage: node build_pptx.mjs spec.json output.pptx [prototype.png]");
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
    const table = slide.tables.add({
      rows: values.length,
      columns: roster.header.length,
      left: 68,
      top: 132,
      width: 1040,
      height: 495,
      columnWidths: [650, 390],
      values,
    });
    for (const [row, cells] of values.entries()) {
      table.rows[row].height = 45;
      for (const [column] of cells.entries()) {
        const cell = table.getCell(row, column);
        cell.fill = row === 0 ? "#EAEAEA" : "#FFFFFF";
        cell.text.style = {
          typeface: theme.font_name,
          fontSize: 21,
          color: `#${theme.body_color}`,
          bold: row === 0,
          verticalAlignment: "middle",
        };
      }
    }
    table.borders.assign({ fill: "#D6D6D6", width: 1, style: "solid" });
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

  slide.speakerNotes.text = item.notes.join("\n\n");
}
await (await PresentationFile.exportPptx(deck)).save(outputPath);
