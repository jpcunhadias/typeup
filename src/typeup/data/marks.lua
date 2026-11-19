-- typeup: pandoc Lua filter for typed-up study notes (LaTeX output).
-- Use it with the header notes-header.tex; docs/syntax.md has the syntax.
--
-- Marks: where a piece of text came from.
-- A blockquote line that starts with a bold bracket label becomes a box:
--   > **[Added]** text        -> markadded
--   > **[Your mark]** text    -> markyour
--   > **[Unclear]** text      -> markunclear  (also "[Unclear: ...]")
--   > **[Anything else]** text -> marksource{Anything else}
-- Several labelled lines in one blockquote (one paragraph, separated by
-- line breaks) become several boxes, in order. A blockquote without a
-- label stays a normal quote. Inline [text]{.unclear} spans get a red
-- highlight. Other output formats pass through untouched.

if not FORMAT:match("latex") then
  return {}
end

local function label_of(inline)
  if inline and inline.t == "Strong" then
    local text = pandoc.utils.stringify(inline)
    return text:match("^%[(.-)%]$")
  end
  return nil
end

local function env_for(label)
  if label == "Added" then return "markadded", nil end
  if label == "Your mark" then return "markyour", nil end
  if label:match("^Unclear") then
    local rest = label:match("^Unclear:%s*(.+)$")
    return "markunclear", rest
  end
  return "marksource", label
end

-- Split a paragraph's inlines into runs, starting a new run at a line break
-- that is followed by a bold [label]
local function split_runs(inlines)
  local runs, current = {}, {}
  local i = 1
  while i <= #inlines do
    local el = inlines[i]
    if (el.t == "SoftBreak" or el.t == "LineBreak") and label_of(inlines[i + 1]) then
      table.insert(runs, current)
      current = {}
    else
      table.insert(current, el)
    end
    i = i + 1
  end
  table.insert(runs, current)
  return runs
end

local function boxed(run)
  local label = label_of(run[1])
  if not label then
    return nil
  end
  local env, extra = env_for(label)
  local body = pandoc.List()
  -- drop the label and the space after it
  local start = 2
  if run[2] and run[2].t == "Space" then start = 3 end
  if extra and env == "markunclear" then
    body:insert(pandoc.Emph(pandoc.Inlines(extra)))
    body:insert(pandoc.Str(":"))
    body:insert(pandoc.Space())
  end
  for k = start, #run do body:insert(run[k]) end
  local open = env == "marksource"
    and ("\\begin{marksource}{" .. extra:gsub("([#$%%&_{}])", "\\%1") .. "}")
    or ("\\begin{" .. env .. "}")
  return { pandoc.RawBlock("latex", open), pandoc.Para(body),
           pandoc.RawBlock("latex", "\\end{" .. env .. "}") }
end

function BlockQuote(bq)
  local out, plain, changed = pandoc.List(), pandoc.List(), false
  local function flush()
    if #plain > 0 then
      out:insert(pandoc.BlockQuote(plain))
      plain = pandoc.List()
    end
  end
  for _, block in ipairs(bq.content) do
    if (block.t == "Para" or block.t == "Plain") and label_of(block.content[1]) then
      for _, run in ipairs(split_runs(block.content)) do
        local blocks = boxed(run)
        if blocks then
          flush()
          out:extend(blocks)
          changed = true
        elseif #run > 0 then
          plain:insert(pandoc.Para(run))
        end
      end
    elseif block.t == "Para" and changed and #plain == 0 and #out > 0 then
      -- a follow-on paragraph inside a labelled quote belongs to the box
      -- above it: reopen that box's content
      local last_end = out:remove()
      out:insert(block)
      out:insert(last_end)
    else
      plain:insert(block)
    end
  end
  flush()
  if changed then return out end
  return nil
end

function Span(span)
  if span.classes:includes("unclear") then
    local inlines = pandoc.List({ pandoc.RawInline("latex", "\\unclearinline{") })
    inlines:extend(span.content)
    inlines:insert(pandoc.RawInline("latex", "}"))
    return inlines
  end
end

-- Fenced divs that say what kind of text a block is:
--   ::: definition                      -> Definition 3
--   ::: {.theorem title="Weak duality"} -> Theorem 4 (Weak duality)
--   ::: {.exercise title="Sheet 5, 3c"} -> Exercise 5 (Sheet 5, 3c)
--   ::: proof                           -> Proof. ... (box at the end)
-- The title may hold Markdown and $maths$. Boxes are defined in
-- notes-header.tex; a div with any other class is left alone.
-- ::: legend at the top of a note: "How to read this note", holding one
-- real, shortened example of each mark the note uses; inside it each box
-- title also says what the mark means (notes-header.tex)
local content_boxes = {
  legend = "notelegend",
  definition = "nbdefinition", theorem = "nbtheorem",
  proposition = "nbproposition", lemma = "nblemma",
  corollary = "nbcorollary", example = "nbexample", remark = "nbremark",
  exercise = "nbexercise", proof = "nbproof",
}

local function latex_title(text)
  if not text or text == "" then return "" end
  local doc = pandoc.read(text, "markdown")
  local blocks = doc.blocks
  if #blocks == 0 then return "" end
  return (pandoc.write(pandoc.Pandoc({ pandoc.Plain(blocks[1].content) }), "latex"):gsub("%s+$", ""))
end

-- Header metadata: course, label and date (YYYY-MM-DD is written out as
-- "Wed 21 Oct 2026", anything else is printed as given)
local months = { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                 "Sep", "Oct", "Nov", "Dec" }
local weekdays = { "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" }

local function format_date(text)
  local y, m, d = text:match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
  if not y then return text end
  local t = os.time({ year = tonumber(y), month = tonumber(m), day = tonumber(d), hour = 12 })
  if not t then return text end
  local wday = os.date("*t", t).wday
  return weekdays[wday] .. " " .. tonumber(d) .. " " .. months[tonumber(m)] .. " " .. y
end

-- A metadata value (or attribute string) as LaTeX: Markdown is rendered,
-- special characters are escaped
local function meta_latex(value, is_date)
  if value == nil then return "" end
  local text
  if type(value) == "string" then
    text = value
  else
    text = pandoc.utils.stringify(value)
  end
  if is_date then text = format_date(text) end
  if text == "" then return "" end
  local doc = pandoc.read(text, "markdown")
  if #doc.blocks == 0 or not doc.blocks[1].content then return "" end
  return (pandoc.write(pandoc.Pandoc({ pandoc.Plain(doc.blocks[1].content) }), "latex"):gsub("%s+$", ""))
end

function Div(div)
  -- typeup combine opens each note with an empty marker div:
  --   ::: {.typeup-note course="..." label="..." date="YYYY-MM-DD"}
  if div.classes:includes("typeup-note") then
    local a = div.attributes
    return pandoc.RawBlock("latex", "\\notebreak{" .. meta_latex(a.course) .. "}{"
      .. meta_latex(a.label) .. "}{" .. meta_latex(a.date, true) .. "}")
  end
  for _, class in ipairs(div.classes) do
    local env = content_boxes[class]
    if env then
      local open = "\\begin{" .. env .. "}"
      if env ~= "notelegend" then
        open = open .. "{" .. latex_title(div.attributes["title"]) .. "}"
      end
      local out = pandoc.List({ pandoc.RawBlock("latex", open) })
      out:extend(div.content)
      out:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
      return out
    end
  end
end

-- Plain ``` code blocks (no language) get the same frame as highlighted
-- ones, which notes-header.tex draws through pandoc's Shaded environment
function CodeBlock(cb)
  if #cb.classes == 0 then
    return { pandoc.RawBlock("latex", "\\begin{codebox}"), cb,
             pandoc.RawBlock("latex", "\\end{codebox}") }
  end
end

-- The course . lecture . date line goes under the first # heading of each
-- note (a combined PDF holds several notes, each opened by \notebreak)
-- Keep-with-next. A heading, or a short lead-in paragraph ("... is:",
-- "**Corollary 3.6.**", "Rearranging gives") must not end a page while
-- the formula, table, list or box it introduces starts the next one.
-- Before such a block: \needspace (start a new page if fewer than a few
-- lines are left); after a lead-in: \nopagebreak.
local function display_math_only(b)
  if b.t ~= "Para" and b.t ~= "Plain" then return false end
  local seen = false
  for _, el in ipairs(b.content) do
    if el.t == "Math" and el.mathtype == "DisplayMath" then seen = true
    elseif el.t ~= "Space" and el.t ~= "SoftBreak" and el.t ~= "LineBreak" then
      return false
    end
  end
  return seen
end

local function introduces(b)
  if not b then return false end
  if display_math_only(b) then return true end
  if b.t == "Table" or b.t == "BulletList" or b.t == "OrderedList"
     or b.t == "CodeBlock" or b.t == "BlockQuote" or b.t == "Figure"
     or b.t == "DefinitionList" then
    return true
  end
  -- a box opened by this filter (content box, mark box, code box)
  if b.t == "RawBlock" and b.text:match("^\\begin{") ~= nil then return true end
  -- another lead-in line ending in ":" (a chain of lead-ins)
  return (b.t == "Para" or b.t == "Plain")
    and pandoc.utils.stringify(b):match(":%s*$") ~= nil
end

local function is_lead_in(b, nxt)
  if (b.t ~= "Para" and b.t ~= "Plain") or display_math_only(b) then
    return false
  end
  if not introduces(nxt) then return false end
  local text = pandoc.utils.stringify(b)
  if display_math_only(nxt) then return true end  -- text, then its formula
  if text:match(":%s*$") then return true end
  -- a bold label on its own ("Corollary 3.6.") or a short lead-in line
  return utf8.len(text) ~= nil and utf8.len(text) < 80
end

-- One pass over a list of blocks; quotes are handled recursively.
-- Headings and lead-ins that follow each other form one run: only the
-- first gets a \needspace, sized for the whole run plus a few lines of
-- what it introduces (a \needspace inside the run would itself allow a
-- break there).
local function keeper(blocks, i)
  local b = blocks[i]
  if not b then return false end
  if b.t == "Header" then return true end
  return is_lead_in(b, blocks[i + 1])
end

local function keep_with_next(blocks, top)
  local out, fresh, in_run = pandoc.List(), top, false
  for i, block in ipairs(blocks) do
    local nxt = blocks[i + 1]
    local opens_note = fresh and block.t == "Header" and block.level == 1
    if block.t == "RawBlock" and block.text:match("^\\notebreak") then
      fresh = true
      in_run = false
      out:insert(block)
    elseif keeper(blocks, i) and not opens_note then
      if not in_run then
        local n = 0
        while keeper(blocks, i + n) do n = n + 1 end
        out:insert(pandoc.RawBlock("latex",
          "\\needspace{" .. (3 + 3 * n) .. "\\baselineskip}"))
      end
      out:insert(block)
      if block.t ~= "Header" then
        out:insert(pandoc.RawBlock("latex", "\\nopagebreak"))
      end
      in_run = keeper(blocks, i + 1)
    else
      in_run = false
      if block.t == "BlockQuote" then
        block.content = keep_with_next(block.content, false)
      end
      out:insert(block)
      if opens_note then
        out:insert(pandoc.RawBlock("latex", "\\notemetaline"))
        fresh = false
      end
    end
  end
  return out
end

function Pandoc(doc)
  doc.blocks = keep_with_next(doc.blocks, true)
  -- a single note: its header from the metadata (typeup fills course,
  -- label and date from the file name unless the note or a flag sets them)
  local m = doc.meta
  -- legend-added / legend-your / legend-unclear / legend-source: what each
  -- mark means, as the legend says it (notes-header.tex has the defaults)
  local roles = { added = "addedrole", your = "yourrole", unclear = "unclearrole",
                  source = "sourcerole" }
  for key, macro in pairs(roles) do
    local value = m["legend-" .. key]
    if value then
      doc.blocks:insert(1, pandoc.RawBlock("latex",
        "\\renewcommand{\\" .. macro .. "}{" .. meta_latex(value) .. "}"))
    end
  end
  if m.course or m.label or m.date then
    doc.blocks:insert(1, pandoc.RawBlock("latex",
      "\\renewcommand{\\notecourse}{" .. meta_latex(m.course) .. "}"
      .. "\\renewcommand{\\notelabel}{" .. meta_latex(m.label) .. "}"
      .. "\\renewcommand{\\notedate}{" .. meta_latex(m.date, true) .. "}"))
  end
  return doc
end

-- Inline code (file paths, function names) may wrap after / _ - . so a
-- long path doesn't run into the right margin
local function tex_escape(s)
  return (s:gsub("[\\{}$&#%%_%^~]", function(c)
    if c == "\\" then return "\\textbackslash{}" end
    if c == "^" then return "\\textasciicircum{}" end
    if c == "~" then return "\\textasciitilde{}" end
    return "\\" .. c
  end))
end

function Code(code)
  local out = {}
  for ch in code.text:gmatch(utf8.charpattern) do
    local t = tex_escape(ch)
    if ch == " " then t = "\\ " end
    if ch == "/" or ch == "_" or ch == "-" or ch == "." then
      t = t .. "\\allowbreak{}"
    end
    out[#out + 1] = t
  end
  return pandoc.RawInline("latex", "\\texttt{" .. table.concat(out) .. "}")
end

-- Short pipe tables get fixed-width columns that never wrap, so one long
-- cell (often a file path) pushes the table off the page. When the widest
-- cells add up to more than about a line, give the columns widths in
-- proportion to their content so they wrap instead.
function Table(tbl)
  -- Widths already set are kept, except the equal ones pandoc derives
  -- from a |---|---| separator when a row is longer than a line
  local first, equal, set = tbl.colspecs[1] and tbl.colspecs[1][2], true, false
  for _, spec in ipairs(tbl.colspecs) do
    if spec[2] and spec[2] ~= 0 then set = true end
    if spec[2] ~= first then equal = false end
  end
  if set and not equal then return nil end
  local n = #tbl.colspecs
  -- maxlen: longest cell per column; maxword: longest piece that can't
  -- wrap (a word, a $formula$, a `path`), so no column gets too narrow
  -- for it
  local maxlen, maxword = {}, {}
  for i = 1, n do maxlen[i] = 3; maxword[i] = 3 end
  local function scan(rows)
    for _, row in ipairs(rows) do
      local col = 1
      for _, cell in ipairs(row.cells) do
        if col <= n then
          local len = utf8.len(pandoc.utils.stringify(cell.contents)) or 0
          -- a file link is already raw LaTeX (Link, below): count its text
          pandoc.walk_block(pandoc.Div(cell.contents), {
            RawInline = function(el)
              local shown = el.text:gsub("\\href%b{}", ""):gsub("\\%a+", ""):gsub("[{}]", "")
              len = len + (utf8.len(shown) or 0)
              for w in shown:gmatch("%S+") do
                maxword[col] = math.max(maxword[col], utf8.len(w) or 0)
              end
            end,
          })
          if len > maxlen[col] then maxlen[col] = len end
          -- an inline formula stays on one line (LaTeX would break it
          -- after "=" in a narrow column)
          cell.contents = pandoc.walk_block(pandoc.Div(cell.contents), {
            Str = function(el) maxword[col] = math.max(maxword[col], utf8.len(el.text) or 0) end,
            Math = function(el)
              if el.mathtype ~= "InlineMath" then return nil end
              maxword[col] = math.max(maxword[col], #el.text)
              return { pandoc.RawInline("latex", "\\mbox{"), el, pandoc.RawInline("latex", "}") }
            end,
          }).content
        end
        col = col + (cell.col_span or 1)
      end
    end
  end
  scan(tbl.head.rows)
  for _, body in ipairs(tbl.bodies) do scan(body.body) end
  local total = 0
  for i = 1, n do total = total + maxlen[i] end
  if total <= 60 then return nil end
  -- about 90 characters fit on a line
  local w, sum = {}, 0
  for i = 1, n do
    w[i] = math.max(0.06, maxlen[i] / total * 0.96, (maxword[i] + 2) / 90)
    sum = sum + w[i]
  end
  for i = 1, n do tbl.colspecs[i][2] = w[i] / sum * 0.96 end
  return tbl
end

-- Links to the course's own files ([the slides](../moodle/slides-05.pdf),
-- written relative to the note): typeup sets TYPEUP_NOTES_DIR to the
-- note's folder, and the link becomes an absolute file link, so it opens
-- from the PDF wherever the PDF is (notes/pdf/, a combined PDF). The PDF
-- then holds that absolute path: typeup --no-file-links leaves the
-- variable unset and links as written. Web links and #anchors are left
-- alone.
local notes_dir = os.getenv("TYPEUP_NOTES_DIR")
if notes_dir == "" then notes_dir = nil end

local function file_url(path)
  return "file://" .. path:gsub("[^%w/%-%._~]", function(c)
    return string.format("%%%02X", string.byte(c))
  end)
end

function Link(link)
  local t = link.target
  if not notes_dir or t == "" or t:match("^#") or t:match("^%a[%w+.-]*:") then
    return nil
  end
  t = t:gsub("%%(%x%x)", function(h) return string.char(tonumber(h, 16)) end)
  local path = t:match("^/") and t or pandoc.path.join({ notes_dir, t })
  local parts = {}
  for part in path:gmatch("[^/]+") do
    if part == ".." then table.remove(parts)
    elseif part ~= "." then table.insert(parts, part) end
  end
  path = "/" .. table.concat(parts, "/")
  -- a PDF: a plain path, which hyperref makes a GoToR link (Preview opens
  -- it; a %20 there would not be decoded); anything else: a file:// URL
  if not path:lower():match("%.pdf$") then
    link.target = file_url(path)
    return link
  end
  -- written as raw \href: pandoc would turn spaces into %20 again
  local text = pandoc.write(pandoc.Pandoc({ pandoc.Plain(link.content) }), "latex"):gsub("%s+$", "")
  local target = path:gsub("[#%%{}\\]", "\\%0")
  return pandoc.RawInline("latex", "\\href{" .. target .. "}{" .. text .. "}")
end
